import numpy as np


def similarity_transform(from_points, to_points):
    """
    References
    - [Umeyama's paper](http://localhost:3690/files/doc/Umeyama_least_square.pdf)
    - [CarloNicolini's python implementation](https://gist.github.com/CarloNicolini/7118015)

    Modified by Kevin Horecka Feb 11, 2017

    :param from_points: a list of points (list of floats) from which to find a transform
    :param to_points: a list points (list of floats) to which to find a transform

    :return: the rotation matrix, scaling, and translation between from_points and to_points via SVD
    """
    assert len(from_points.shape) == 2, \
        "from_points must be a m x n array"
    assert from_points.shape == to_points.shape, \
        "from_points and to_points must have the same shape"

    N, m = from_points.shape

    mean_from = from_points.mean(axis=0)
    mean_to = to_points.mean(axis=0)

    delta_from = from_points - mean_from  # N x m
    delta_to = to_points - mean_to  # N x m

    sigma_from = (delta_from * delta_from).sum(axis=1).mean()
    # sigma_to = (delta_to * delta_to).sum(axis=1).mean()

    cov_matrix = delta_to.T.dot(delta_from) / N

    U, d, V_t = np.linalg.svd(cov_matrix, full_matrices=True)
    cov_rank = np.linalg.matrix_rank(cov_matrix)
    S = np.eye(m)

    if cov_rank >= m - 1 and np.linalg.det(cov_matrix) < 0:
        S[m - 1, m - 1] = -1
    elif cov_rank < m - 1:
        raise ValueError("colinearility detected in covariance matrix:\n{}".format(cov_matrix))

    R_out = U.dot(S).dot(V_t)
    c_out = (d * S.diagonal()).sum() / sigma_from
    t_out = mean_to - c_out * R_out.dot(mean_from)

    return R_out, c_out, t_out


if __name__ == "__main__":
    # Testing case from the original paper by Umeyama.
    # each row represents a point
    f_points = np.array([[0, 0],
                         [1, 0],
                         [0, 2]])
    t_points = np.array([[0, 0],
                         [-1, 0],
                         [0, 2]])

    c_ans = 0.721
    R_ans = np.array([[0.832, 0.555],
                      [-0.555, 0.832]])
    t_ans = np.array([-0.8, 0.4])
    M_ans = c_ans * R_ans

    R, c, t = similarity_transform(f_points, t_points)
    assert np.allclose(c*R, M_ans, atol=1e-3) and np.allclose(t, t_ans, atol=1e-3), "test from Umeyama's paper fail"
    print("test from Umeyama's paper pass")

    # test in 3D space
    f_points = np.array([[0, 0, 1],
                         [1, 0, 3],
                         [2, 5, 8]])

    M_ans = np.array([[0, -1, 0],
                      [1, 0, 0],
                      [0, 0, 1]])
    t_ans = np.array([1, 1, 1])

    t_points = M_ans.dot(f_points.T).T + t_ans

    R, c, t = similarity_transform(f_points, t_points)
    assert np.allclose(c*R, M_ans) and np.allclose(t, t_ans), "test for 3D space fail"
    print("test for 3D space pass")
