from wmbench.quality.metrics import psnr

target = 40.0
tolerance = 0.1
scale_low = 24.0
scale_high = 250.0
search_steps = 12


def alpha_for(psnr_now, psnr_target=target):
    return 10 ** ((psnr_now - psnr_target) / 20)


def match_additive(wm, img, bits, psnr_target=target):
    strength = wm.native_strength
    marked = wm.embed(img, bits, strength)
    value = psnr(img, marked)
    tries = [(strength, value, marked)]
    for i in range(2):
        if abs(value - psnr_target) <= tolerance:
            break
        strength = strength * alpha_for(value, psnr_target)
        marked = wm.embed(img, bits, strength)
        value = psnr(img, marked)
        tries.append((strength, value, marked))
    return min(tries, key=lambda t: abs(t[1] - psnr_target))


def match_scale(wm, img, bits, psnr_target=target):
    low = scale_low
    high = scale_high
    best = None
    for i in range(search_steps):
        mid = (low + high) / 2
        marked = wm.embed(img, bits, mid)
        value = psnr(img, marked)
        if best is None or abs(value - psnr_target) < abs(best[1] - psnr_target):
            best = (mid, value, marked)
        if abs(value - psnr_target) <= tolerance:
            break
        if value > psnr_target:
            low = mid
        else:
            high = mid
    return best


def match(wm, img, bits, psnr_target=target):
    if wm.name == "dwtdct":
        return match_scale(wm, img, bits, psnr_target)
    return match_additive(wm, img, bits, psnr_target)
