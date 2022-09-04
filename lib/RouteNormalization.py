def normalize(ds: list, delta_hs: list, Psis: list, segment_len=10):
    assert len(ds) == len(delta_hs)
    new_ds = []
    new_delta_hs = []
    new_Psis = []

    while len(ds) > 0:
        new_d = 0
        new_delta_h = 0

        while len(ds) > 0:
            d = ds.pop(0)
            delta_h = delta_hs.pop(0)
            Psi = Psis.pop(0)

            if d + new_d >= segment_len:
                required_dist = segment_len - new_d
                required_factor = required_dist / d

                new_d += d * required_factor
                new_delta_h += delta_h * required_factor

                d *= (1 - required_factor)
                delta_h *= (1 - required_factor)

                new_ds.append(new_d)
                new_delta_hs.append(new_delta_h)
                new_Psis.append(Psi)
                ds = [d] + ds
                delta_hs = [delta_h] + delta_hs
                Psis = [Psi] + Psis
                break
            else:
                new_d += d
                new_delta_h += delta_h

            if len(ds) == 0:
                new_ds.append(new_d)
                new_delta_hs.append(new_delta_h)
                new_Psis.append(Psi)

    return new_ds, new_delta_hs, new_Psis
