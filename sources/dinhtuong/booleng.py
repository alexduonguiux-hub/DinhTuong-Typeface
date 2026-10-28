"""Evaluate a glyph's boolean op list into clean, non-overlapping contours.

Semantics mirror preview.render_ops / the Figma build:
    result = {} ; add -> result |= c ; sub -> result -= c ; group -> result |= eval(group)
Engine: booleanOperations (flatten -> Clipper -> curve re-fit), built locally from source.
Contours use the geo.py segment format: ('M',x,y) ('L',x,y) ('C',x1,y1,x2,y2,x,y) ('Z',).
"""
from booleanOperations import BooleanOperationManager as BOM
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.pointPen import PointToSegmentPen


def _area(segs):
    from geo import flatten
    p = flatten(segs, 8)
    return sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p))) / 2


class _C:
    """minimal contour object exposing drawPoints() for booleanOperations.
    norm=True: raw construction contour -> force one winding so overlaps union (nonzero)."""
    def __init__(self, segs, norm=False):
        self.segs = segs
        self.rev = norm and _area(segs) > 0   # match Clipper output (outer = CCW)

    def __len__(self):
        return len(self.segs)

    def draw(self, pen):
        started = False
        for s in self.segs:
            k = s[0]
            if k == 'M':
                if started:
                    pen.closePath()
                pen.moveTo((s[1], s[2])); started = True; last = (s[1], s[2]); first = last
            elif k == 'L':
                if (s[1], s[2]) != last:
                    pen.lineTo((s[1], s[2])); last = (s[1], s[2])
            elif k == 'C':
                pen.curveTo((s[1], s[2]), (s[3], s[4]), (s[5], s[6])); last = (s[5], s[6])
            elif k == 'Z':
                pen.closePath(); started = False
        if started:
            pen.closePath()

    def drawPoints(self, ppen):
        from fontTools.pens.reverseContourPen import ReverseContourPen
        pen = SegmentToPointPen(ppen)
        self.draw(ReverseContourPen(pen) if self.rev else pen)


def _to_segs(rec):
    """RecordingPen value -> list of contours in segment format."""
    out, cur = [], None
    for op, args in rec.value:
        if op == 'moveTo':
            cur = [('M',) + tuple(args[0])]
        elif op == 'lineTo':
            cur.append(('L',) + tuple(args[0]))
        elif op == 'curveTo':
            pts = args
            if len(pts) == 3:
                cur.append(('C',) + tuple(pts[0]) + tuple(pts[1]) + tuple(pts[2]))
            else:  # should not happen (cubic input)
                for p in pts[-1:]:
                    cur.append(('L',) + tuple(p))
        elif op == 'qCurveTo':
            cur.append(('L',) + tuple(args[-1]))
        elif op in ('closePath', 'endPath'):
            cur.append(('Z',)); out.append(cur); cur = None
    return out


class _CollectPen(PointToSegmentPen):
    def __init__(self):
        self.rec = RecordingPen()
        super().__init__(self.rec)


def _run(fn, *args):
    pen = _CollectPen()
    fn(*args, pen)
    return _to_segs(pen.rec)


def _split(segs):
    """a contour list may hold several sub-paths (M..Z M..Z)."""
    out, cur = [], []
    for s in segs:
        cur.append(s)
        if s[0] == 'Z':
            out.append(cur); cur = []
    if cur:
        out.append(cur + [('Z',)])
    return out


def evaluate(ops, clean=True):
    res = _evaluate(ops)
    if clean:
        import outline_clean
        res = outline_clean.clean(res)
    return res


def _evaluate(ops):
    res = []
    for op, c in ops:
        if op == 'group':
            g = _evaluate(c)
            if g:
                res = _run(BOM.union, [_C(x) for x in res + g]) if res else _run(BOM.union, [_C(x) for x in g])
        elif op == 'add':
            parts = _split(c)
            res = _run(BOM.union, [_C(x) for x in res] + [_C(x, True) for x in parts])
        elif op == 'sub':
            if res:
                res = _run(BOM.difference, [_C(x) for x in res], [_C(x, True) for x in _split(c)])
    return res
