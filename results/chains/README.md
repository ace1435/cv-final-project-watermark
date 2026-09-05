# Chains of sharing actions

## What this transform is

Five named sequences of actions that imitate how an image actually travels between people. Each
step records its parameters and the chain composes them, so the oracle inverse of the whole chain
still exists.

| Chain | Steps |
|---|---|
| chain_desktop_whatsapp | Windows 125 percent screenshot, then the WhatsApp Android profile |
| chain_phone_instagram | Pixel 7 screenshot, then a centre crop to 4 by 5, then the Instagram profile |
| chain_crop_jpeg_screenshot | crop keeping 70 percent, JPEG q85, then a 110 percent desktop screenshot |
| chain_double_screenshot | a 110 percent screenshot, then a 90 percent screenshot of that |
| chain_telegram_caption_twitter | the Telegram profile, then a 10 percent caption band, then the Twitter profile |

## What to look for

Chains stack two or three losses. Compare each chain with its single actions in the other
folders to see whether the losses add up or whether one step dominates. The strip ends with the
phone to Instagram chain put back into the original grid, where the valid mask shows the area
lost to the centre crop.

## Files

- `samples/` holds one strip per smoke image for three images.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show the pixels after each chain and that the composed inverse works.
