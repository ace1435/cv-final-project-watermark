# Watermarkers

One adapter per method, all with the same interface. Images are uint8 RGB arrays of shape
`(H, W, 3)`. Messages are arrays of 0 and 1 of length `nbits`.

- `embed(img, bits, strength)` returns the watermarked image as uint8 RGB.
- `decode(img, strength=None)` returns one score per bit, positive for a 1 bit. Learned methods
  return decoder logits and ignore `strength`. The classical method needs the quantisation step
  it was embedded with, so the runner passes the strength stored in the item record.
- `native_strength` is the value of the strength knob the authors ship as default.
- `residual(img, bits, strength=None)` returns the float difference between the watermarked
  image and the cover.
- `random_bits(rng)` draws a message for one image from a seeded generator.

`load(name)` in `__init__.py` builds an adapter by name. `primaries` lists the five benchmark
methods in order.

| Name | Bits | Strength knob | Native | Decoder input | Extra outputs |
|---|---|---|---|---|---|
| `dwtdct` | 32 | quantisation step `scales` | 36 | full image, U channel of YUV | none |
| `trustmark_q` | 100 raw | `WM_STRENGTH` | 1.0 | resized to 245 px square by the library | `ecc_ok`, whether the BCH payload decodes |
| `wam` | 32 | `scaling_w` | 2.0 | resized to 256 px square by the library | `pixel_score`, fraction of pixels flagged as watermarked |
| `pixelseal` | 256 | `blender.scaling_w` | 0.2 | resized to 256 px square by the library | `detect_logit`, the detection bit of the decoder |
| `hidden` | 48 | external factor on the residual | 1.0 | full image | none |
| `videoseal_1` | 256 | `blender.scaling_w` | 0.2 | as pixelseal | sanity twin of pixelseal, not a primary |

## Method notes

`dwtdct` wraps `EmbedDwtDctSvd` from invisible-watermark 0.2.0, the DCT plus SVD variant. The
library returns hard bits, so a subclass repeats its decode loop and returns the mean block vote
per bit before the final threshold, mapped to the range from -1 to 1. Embedding writes float
wavelet coefficients back into a uint8 array, so saturated colours wrap and a few photos sit far
below 40 dB at every step. Steps below 24 quantise more finely than the uint8 rounding noise of
the colour conversion and stop decoding, so the strength search never goes below 24. On mostly
white screens the modulation clips at 255 and the method often fails at the default step.

`trustmark_q` uses TrustMark 0.9.1, variant Q, with `use_ECC=False` so that all 100 raw bits
are visible. Messages are BCH codewords of a random 61 bit payload made with the library data
layer, so raw bit accuracy is measured against the codeword and `ecc_ok` reports whether the
payload survives. Logits come from `decoder.decoder` after the library resize to 245 px. The
model files are fetched by the package on first use into its own folder and checked by md5.

`wam` builds Watermark Anything from the pinned repository under `third_party` with the MIT
checkpoint. The message score is the mean of the per pixel bit logits weighted by the sigmoid of
the mask logit, and `pixel_score` is the fraction of pixels whose mask sigmoid exceeds 0.5. The
strength knob is `scaling_w`, applied before the JND attenuation of the library.

`pixelseal` builds the PixelSeal model from the VideoSeal package with the card values and the
checkpoint downloaded by `environment/download_models.py`. The pip installed package ships no
config files, so the model is assembled from the card directly. Embedding runs in the Y channel
with JND attenuation, and the detector returns one detection logit and 256 bit logits.

`hidden` loads the 48 bit TorchScript encoder and decoder that Meta released with Stable
Signature. Inputs use ImageNet normalisation, messages are mapped to -1 and 1, and the strength
factor scales the residual before clipping and rounding.
