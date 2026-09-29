"""Fit instructions to the actual display before the experiment clock starts.

Trial cubes retain their configured visual degrees. No layout runs per frame.
"""
MARGIN_FRACTION = 0.05
TEXT_NAMES = ('text_3', 'text_9', 'text_11', 'text_12', 'text_13', 'text_14',
              'text_16', 'text_18', 'text_19', 'text_23', 'text_25', 'text_27')
IMAGE_NAMES = ('image4', 'image_5', 'image_6', 'image_7', 'image_8')


def safe_size(size):
    return tuple(float(v) * (1 - 2 * MARGIN_FRACTION) for v in size)


def _pixels(stim, value):
    from psychopy.tools.monitorunittools import convertToPix
    import numpy as np
    return np.asarray(convertToPix(np.asarray(value), np.zeros(2),
                                  stim.units, stim.win), dtype=float)


def bounds(stim):
    """Conservative pixel bounds with room for glyph overhangs."""
    if hasattr(stim, 'boundingBox'):
        stim.setText(log=False)
        pad = max(6, float(_pixels(stim, (0, stim.height))[1]) * .25)
        width, height = (float(v) + pad for v in stim.boundingBox)
    else:
        width, height = _pixels(stim, stim.size)
    x, y = _pixels(stim, stim.pos)
    return x - width / 2, y - height / 2, x + width / 2, y + height / 2


def _size(stim):
    l, b, r, t = bounds(stim)
    return r - l, t - b


def _scale(stim, factor, scale_wrap=True):
    if hasattr(stim, 'boundingBox'):
        stim.setHeight(stim.height * factor, log=False)
        if scale_wrap:
            stim.wrapWidth = stim.wrapWidth * factor
        stim.setText(log=False)
    else:
        stim.setSize(stim.size * factor, log=False)


def _position(stim, x, y):
    factor = _pixels(stim, (1, 1))
    stim.setPos((x / factor[0], y / factor[1]), log=False)


def _wrap(stim, width):
    factor = float(_pixels(stim, (1, 0))[0])
    pad = max(12, float(_pixels(stim, (0, stim.height))[1]) * .5)
    stim.wrapWidth = min(stim.wrapWidth, (width - pad) / factor)
    stim.setText(log=False)


def fit_presentation(win, components):
    width, height = safe_size(win.size)
    for name in TEXT_NAMES:
        stim = components[name]
        _wrap(stim, width)
        for _ in range(12):
            w, h = _size(stim)
            factor = min(1, width / max(1, w), height / max(1, h))
            if factor >= 1:
                break
            _scale(stim, factor * .98, scale_wrap=False)
        _position(stim, 0, 0)

    # Fit each simultaneous text/illustration pair together, with a visible gap.
    for tn, im in (('text_22', 'image_9'), ('text_24', 'image_10')):
        text, image = components[tn], components[im]
        _wrap(text, width)
        gap = float(win.size[1]) * .025
        for _ in range(12):
            tw, th = _size(text)
            iw, ih = _size(image)
            factor = min(1, width / max(tw, iw), (height - gap) / (th + ih))
            if factor >= 1:
                break
            _scale(text, factor * .98)
            _scale(image, factor * .98)
        _, th = _size(text)
        _, ih = _size(image)
        _position(text, 0, (ih + gap) / 2)
        _position(image, 0, -(th + gap) / 2)

    for name in IMAGE_NAMES:
        stim = components[name]
        w, h = _size(stim)
        factor = min(1, width / w, height / h)
        if factor < 1:
            _scale(stim, factor)

    names = (*TEXT_NAMES, *IMAGE_NAMES, 'text_22', 'image_9', 'text_24', 'image_10',
             'image_2', 'image_3', 'image_4')
    for name in names:
        left, bottom, right, top = bounds(components[name])
        if (left < -width / 2 - 1 or right > width / 2 + 1 or
                bottom < -height / 2 - 1 or top > height / 2 + 1):
            print(f'Presentation bounds: {name} {(left, bottom, right, top)}, safe size {(width, height)}')
            raise RuntimeError('Content cannot fit within the display margins. Check the '
                               'monitor calibration, display size and cube size in File > Settings.')
