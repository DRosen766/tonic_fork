import numpy as np


# Code taken from https://github.com/uzh-rpg/rpg_e2vid/blob/master/utils/inference_utils.py#L431
def to_voxel_grid_numpy(events, sensor_size, n_time_bins=10):
    """Build a voxel grid with bilinear interpolation in the time domain from a set of events.

    Parameters:
        events: ndarray of shape [num_events, num_event_channels]
        sensor_size: size of the sensor that was used [W,H].
        n_time_bins: number of bins in the temporal axis of the voxel grid.

    Returns:
        numpy array of n event volumes (n,w,h,t)

    """
    assert "x" and "y" and "t" and "p" in events.dtype.names

    voxel_grid = np.zeros((n_time_bins, sensor_size[1], sensor_size[0]), float).ravel()

    # normalize the event timestamps so that they lie between 0 and n_time_bins
    last_stamp = events["t"][-1]
    first_stamp = events["t"][0]
    deltaT = last_stamp - first_stamp

    if deltaT == 0:
        deltaT = 1.0

    events["t"] = (n_time_bins) * (events["t"] - first_stamp) / deltaT
    ts = events["t"]
    xs = events["x"].astype(int)
    ys = events["y"].astype(int)
    pols = events["p"]
    pols[pols == 0] = -1  # polarity should be +1 / -1

    tis = ts.astype(int)
    dts = ts - tis
    vals_left = pols * (1.0 - dts)
    vals_right = pols * dts

    valid_indices = tis < n_time_bins
    np.add.at(
        voxel_grid,
        xs[valid_indices]
        + ys[valid_indices] * sensor_size[0]
        + tis[valid_indices] * sensor_size[0] * sensor_size[1],
        vals_left[valid_indices],
    )

    valid_indices = (tis + 1) < n_time_bins
    np.add.at(
        voxel_grid,
        xs[valid_indices]
        + ys[valid_indices] * sensor_size[0]
        + (tis[valid_indices] + 1) * sensor_size[0] * sensor_size[1],
        vals_right[valid_indices],
    )

    voxel_grid = np.reshape(voxel_grid, (n_time_bins, sensor_size[0], sensor_size[1]))

    return voxel_grid
