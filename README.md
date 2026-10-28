# Dinh Tuong

![Dinh Tuong specimen](documentation/specimen.png)

Dinh Tuong is a display typeface drawn from the cast-steel stencil lettering of the shop signs and gate signs of 1960s Saigon. Every glyph is built from rules, with ruler and compass only. The Vietnamese marks are cut from the same strip as the letters rather than added on top.

- 3 weights: Regular, Medium, Bold
- Character set: GF Latin Core + GF Latin Vietnamese (Vietnamese, English, French, Spanish, Polish, Czech, Slovak, Hungarian, Romanian, Turkish, Latvian, Lithuanian, Maltese, German and more)
- Tabular figures (`tnum`)

## Tiếng Việt

Dinh Tuong là kiểu chữ trưng bày dựng theo chữ khuôn thép đúc trên biển hiệu, biển cổng Sài Gòn thập niên 1960. Mỗi glyph dựng theo luật, chỉ bằng thước và compa. Dấu tiếng Việt cắt từ cùng một tấm thép với chữ, không gắn thêm.

- 3 độ đậm: Regular, Medium, Bold
- Bảng chữ: GF Latin Core + GF Latin Vietnamese (tiếng Việt, Anh, Pháp, Tây Ban Nha, Ba Lan, Séc, Slovak, Hungary, Romania, Thổ Nhĩ Kỳ, Latvia, Litva, Malta, Đức…)
- Số đều bề ngang (`tnum`)
- Dựng font: `make build` (mã nguồn là các bộ sinh chữ Python trong `sources/`)
- Giấy phép: SIL Open Font License 1.1

## Building

The fonts are built from the UFO sources in `sources/ufo` with [gftools builder](https://github.com/googlefonts/gftools) (fontmake), configured in `sources/config.yaml`:

```sh
make build        # fonts/ttf, fonts/otf from sources/ufo (gftools builder + fontmake)
make compare      # the build must match the generators' reference binaries (sources/reference/fonts)
make test         # fontspector, Google Fonts profile (needs fontspector)
make proof        # HTML proofs (needs diffenator3)
```

The UFOs themselves are written by the rule-based Python generators in `sources/dinhtuong/`, which draw every glyph from its construction rules (ruler and compass only), space and kern it, and compile reference binaries:

```sh
make generate     # = sh sources/generate.sh -> sources/ufo + sources/reference/fonts
```

Requirements are pinned in `requirements.txt` (Python 3.11 or later).

## Changelog

See `documentation/CHANGELOG.md`.

## License

This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at https://openfontlicense.org

## Repository layout

This font repository follows the [Google Fonts project template](https://github.com/googlefonts/googlefonts-project-template):

- `sources/`: UFO build sources, gftools builder config, the rule-based generators and their reference binaries
- `fonts/`: the font binaries, one folder per format
- `documentation/`: specimen, article and changelog
