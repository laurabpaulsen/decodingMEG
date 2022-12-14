"""
Decoding class used for Bachelor's thesis.

Author: Laura Bock Paulsen
"""
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

class Decoder():
    def __init__(self, classification, alpha, ncv, scale, model_type = 'LDA', get_tgm = True):
            self.classification = classification
            self.alpha = alpha
            self.ncv = ncv
            self.scale = scale
            self.model_type = model_type
            self.get_tgm = get_tgm

    
    def check_y_format(self,y):
        y = np.copy(y)
        y = y * 1 # convert to int if it was Boolean 
        if not self.classification:
            y = y.astype(float)
            return y

        y = y.astype(int)
        values = np.unique(y)
        ycopy = np.copy(y)
        for k in range(len(values)):
            y[ycopy == values[k]] = k+1

        return y

    
    def train_test_decoding(self, X_train, y_train, X_test, y_test):
        T = X_train.shape[0] # T = time

        y_train = self.check_y_format(y_train)
        y_test = self.check_y_format(y_test)

        if self.get_tgm:
            scores = np.zeros((T,T))
                
        elif not self.get_tgm:
            scores = np.zeros(T)

        for t in range(T):
            X_t = X_train[t, :, :]
            if self.model_type == 'LDA':
                model = make_pipeline(StandardScaler(), LDA(solver = 'lsqr', shrinkage = self.alpha))
            elif self.model_type == 'RidgeClassifier':
                model = make_pipeline(StandardScaler(), RidgeClassifier(solver = 'lsqr'), shrinkage = self.alpha)
            else:
                print('Decoder only supports LDA, SVM or RidgeClassifier')

            model.fit(X_t, y_train)

            if self.get_tgm:
                for t2 in range(T):
                    X_t2 = X_test[t2, :, :]
                    scores[t, t2] = model.score(X_t2, y_test)

            elif not self.get_tgm:
                X_t2 = X_test[t, :, :]
                scores[t] = model.score(X_t2, y_test)

        return scores


    def run_decoding_across_sessions(self, X_train, y_train, X_test, y_test):
        T, N_train, C  = X_train.shape # T = time, N = trials, C = channels
        T, N_test, C = X_test.shape # T = time, N = trials, C = channels


        y_train = self.check_y_format(y_train)
        y_test = self.check_y_format(y_test)

        inds_train = np.array(range(N_train))
        inds_test = np.array(range(N_test))
        np.random.shuffle(inds_train)
        np.random.shuffle(inds_test)

        if self.get_tgm:
            scores = np.zeros((T,T, self.ncv))
                
        elif not self.get_tgm:
            scores = np.zeros((T, self.ncv))

        for c in range(self.ncv):
            inds_tmp_train = inds_train[:]
            inds_tmp_train = np.delete(inds_tmp_train, slice(int(len(inds_tmp_train)/self.ncv) * c, int(len(inds_tmp_train)/self.ncv)*(c+1)))
            
            inds_tmp_test = inds_test[int(len(inds_test)/self.ncv) * c : int(len(inds_test)/self.ncv)*(c+1)]

            X_train_tmp = np.delete(X_train, inds_tmp_train, axis=1)
            y_train_tmp = np.delete(y_train, inds_tmp_train)

            X_test_tmp = X_test[:, inds_tmp_test, :]
            y_test_tmp = y_test[inds_tmp_test]

            for t in range(T):
                X_t = X_train_tmp[t, :, :]

                if self.model_type == 'LDA':
                    model = make_pipeline(StandardScaler(), LDA(solver = 'lsqr', shrinkage = self.alpha))
                elif self.model_type == 'RidgeClassifier':
                    model = make_pipeline(StandardScaler(), RidgeClassifier(solver = 'lsqr'), shrinkage = self.alpha)
                else:
                    print('Decoder only supports LDA, SVM or RidgeClassifier')

                model.fit(X_t, y_train_tmp)

                if self.get_tgm:
                    for t2 in range(T):
                        X_t2 = X_test_tmp[t2, :, :]
                        scores[t, t2, c] = model.score(X_t2, y_test_tmp)

                elif not self.get_tgm:
                    X_t2 = X_test_tmp[t, :, :]
                    scores[t, c] = model.score(X_t2, y_test_tmp)
                    
            if self.get_tgm:        
                accuracies = np.mean(scores, axis = 2)

            elif not self.get_tgm:
                accuracies = np.mean(scores, axis = 1)


        return accuracies


