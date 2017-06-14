import keras.backend as k
import tensorflow as tf
import unittest

from src.attackers.virtual_adversarial import VirtualAdversarialMethod
from src.classifiers import cnn
from src.utils import load_mnist, get_labels_np_array


class TestVirtualAdversarial(unittest.TestCase):
    def test_mnist(self):
        session = tf.Session()
        k.set_session(session)

        # get MNIST
        batch_size, nb_train, nb_test = 100, 1000, 100
        (X_train, Y_train), (X_test, Y_test) = load_mnist()
        X_train, Y_train = X_train[:nb_train], Y_train[:nb_train]
        X_test, Y_test = X_test[:nb_test], Y_test[:nb_test]
        im_shape = X_train[0].shape

        # get classifier
        model = cnn.cnn_model(im_shape, act="relu")
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(X_train, Y_train, epochs=1, batch_size=batch_size, verbose=0)
        scores = model.evaluate(X_test, Y_test)
        print("\naccuracy on test set: %.2f%%" % (scores[1] * 100))

        df = VirtualAdversarialMethod(model, sess=session, clip_min=0., clip_max=1.)
        x_test_adv = df.generate(X_test)
        self.assertFalse((X_test == x_test_adv).all())

        y_pred = get_labels_np_array(model.predict(x_test_adv))
        self.assertFalse((Y_test == y_pred).all())

        scores = model.evaluate(x_test_adv, Y_test)
        print('\naccuracy on adversarial examples: %.2f%%' % (scores[1] * 100))

if __name__ == '__main__':
    unittest.main()