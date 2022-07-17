import math


def gaussian_pdf(x, mu, sigma):
    return 1 / (math.sqrt(2 * math.pi) * sigma) * math.exp(-.5 * ((x - mu) / sigma) ** 2)


def gaussian_cdf(x, mu, sigma):
    return .5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def smooth_truncated_gaussian(ds: list, delta_hs: list, sigma, width):
    def truncated_gaussian_weight(x, a, b):
        mu = 0
        normalization = gaussian_cdf(mu + b, mu, sigma) - gaussian_cdf(mu - a, mu, sigma)
        return gaussian_pdf(x, mu, sigma) / normalization

    new_delta_hs = []

    assert len(ds) == len(delta_hs)
    for i in range(len(ds)):
        # Get actual width and distances from centre to centre
        left_index = right_index = i
        left_dist = right_dist = 0
        distances = dict()
        distances[i] = 0
        while True:
            if left_index - 1 < 0:
                break
            else:
                left_index -= 1
                distances[left_index] = left_dist + ds[left_index] / 2 + ds[i] / 2
                left_dist += ds[left_index]
                if left_dist >= width / 2:
                    break

        while True:
            if right_index + 1 > len(ds) - 1:
                break
            else:
                right_index += 1
                distances[right_index] = right_dist + ds[right_index] / 2 + ds[i] / 2
                right_dist += ds[right_index]
                if right_dist >= width / 2:
                    break

        # Calculate weights for segments:
        weights = dict()
        weight_sum = 0
        for index, dist in distances.items():
            weight = truncated_gaussian_weight(dist, left_dist, right_dist)
            weights[index] = weight
            weight_sum += weight

        # Update delta_h
        new_delta_h = 0
        for index, weight in weights.items():
            new_delta_h += delta_hs[index] * weight / weight_sum
        new_delta_hs.append(new_delta_h)

    return ds, new_delta_hs
