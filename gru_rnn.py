#!/usr/bin/env python
import numpy as np
import util
import theano
import theano.tensor as T

class GruRnn(object):
    def __init__(self, n_in, n_embedding, n_hidden, orthogonal_init):
        self.Wx = util.sharedMatrix(n_in, n_embedding, 'Wx', orthogonal_init)
        self.Wz = util.sharedMatrix(n_in, n_hidden, 'Wz', orthogonal_init)
        self.Wr = util.sharedMatrix(n_in, n_hidden, 'Wr', orthogonal_init)
        self.Ux = util.sharedMatrix(n_hidden, n_embedding, 'Ux', orthogonal_init)
        self.Uz = util.sharedMatrix(n_hidden, n_hidden, 'Uz', orthogonal_init)
        self.Ur = util.sharedMatrix(n_hidden, n_hidden, 'Ur', orthogonal_init)
        self.Wy = util.sharedMatrix(n_in, n_hidden, 'Wy', orthogonal_init)

    def params(self):
        return [self.Wx, self.Wz, self.Wr, self.Ux, self.Uz, self.Ur, self.Wy]

    def recurrent_step(self, x_t, h_t_minus_1):
        # calc reset gate activation
        r = T.nnet.sigmoid(self.Wr[x_t] + T.dot(self.Ur, h_t_minus_1))
        # calc candidate next hidden state (with reset 'r')
        embedding = self.Wx[x_t]
        h_t_candidate = T.tanh(r * h_t_minus_1 + T.dot(self.Ux, embedding))

        # calc update gate activation 
        z = T.nnet.sigmoid(self.Wz[x_t] + T.dot(self.Uz, h_t_minus_1))
        # calc hidden state as affine combo of last state and candidate next state
        h_t = (1 - z) * h_t_minus_1 + z * h_t_candidate

        # calc output; softmax over output weights dot hidden state
        y_t = T.flatten(T.nnet.softmax(T.dot(self.Wy, h_t)), 1)

        # return what we want to have per output step
        return [h_t, y_t]

    def t_y_softmax(self, x, h0):
        [_hs, y_softmax], _ = theano.scan(fn=self.recurrent_step,
                                             sequences=[x],
                                             outputs_info=[h0, None])
        # we return h0 to denote no additional debugging info supplied with softmax
        # TODO fix this; super clumsy api
        return y_softmax, h0
