from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier




pipe_lasso = Pipeline([
    ('scale', StandardScaler()),
    ('clf', LogisticRegression(penalty='l1', solver='saga', class_weight='balanced'))
])

pipe_ridge = Pipeline([
    ('scale', StandardScaler()),
    ('clf', LogisticRegression(penalty='l2', solver='saga', class_weight='balanced'))
])
pipe_elasticnet = Pipeline([
    ('scale', StandardScaler()),
    ('clf', LogisticRegression(penalty='elasticnet', l1_ratio=0.5, solver='saga', class_weight='balanced'))
])
pipe_SVC = Pipeline([
    ('scale', StandardScaler()),
    ('clf', SVC(probability=True))
])
pipe_GB = Pipeline([
    ('scale', StandardScaler()),
    ('clf', GradientBoostingClassifier())
])
pipe_mlp = Pipeline([
    ('scale', StandardScaler()),
    ('clf', MLPClassifier())
])
pipe_RandomForest = Pipeline([
    ('scale', StandardScaler()),
    ('clf', RandomForestClassifier())
])

