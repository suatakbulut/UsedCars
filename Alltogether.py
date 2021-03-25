from sklearn import base 
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer 
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error
import dill 
from datetime import datetime 
import numpy as np

class GroupbyEstimator(base.BaseEstimator, base.RegressorMixin):    
    def __init__(self, column, estimator_factory, predictor, param_grid):
        self.col = [column]
        self.est = {} 
        self.estimator_factory = estimator_factory
        self.predictor = predictor
        self.param_grid = param_grid
    
    def fit(self, X, y):
        grouped = X.groupby(self.col)
        for group in grouped.groups:
            X_group = X.loc[grouped.groups[group]]
            X_group = X_group.drop(self.col, axis=1)
            y_group = y.loc[grouped.groups[group]]
            self.est[group] = self.estimator_factory(self.predictor, self.param_grid)
            self.est[group].fit(X_group, y_group)            
        
        return self
    
    def predict(self, X): 
        grouped = X.groupby(self.col)
        preds_df = pd.DataFrame(index=X.index.copy(), columns=['preds'])
        for group in grouped.groups:
            X_test_group = X.loc[grouped.groups[group]]
            X_test_group = X_test_group.drop(self.col, axis=1)
            preds_df.loc[grouped.groups[group], 'preds'] = self.est[group].predict(X_test_group)
        
        return np.array(preds_df.preds).reshape(1,-1)[0]

def estimator_factory(predictor, param_grid):
    if predictor == 'lin':
        model = LinearRegression()
    elif predictor == 'forest':
        model = RandomForestRegressor()
    else:
        model = Ridge()
    
    pipe = Pipeline(steps = [ 
            ('preprocess', preprocessor),
            ('predictor', model)
        ])
    
    return GridSearchCV(pipe, param_grid, n_jobs=-1, scoring = 'neg_mean_absolute_error')

def result(model, model_name):
    y_pred = model.predict(X_cv) 
    mae_score = round(mean_absolute_error(y_cv, y_pred))
    score = round(model.score(X_cv, y_cv),4)
    print(f'CV - {model_name} Model - R2 Score: {score}') 
    print( f'CV - {model_name} Model - MAE Score: {mae_score}') 

    y_val_pred = model.predict(X_val) 
    score_val = round(model.score(X_val, y_val),4)
    mae_val = round(mean_absolute_error(y_val, y_val_pred))
    print(f'Val - {model_name} Model - R2 Score: {score_val}') 
    print(f'Val - {model_name} Model - MAE Score: {mae_val}') 
    
    dill.dump(model, open(f'../static/model/{model_name}_r2_{score}_mae_{mae_score}.dill', 'wb')) 


if __name__ == '__main__':
    from prepare_dataset import prepare_dataset 
    print('Preparing dataset')
    df = prepare_dataset()
    print('Data imported')

    y = df.price
    X = df.drop("price", axis=1)

    numerical_cols   = [col for col in X.columns if X[col].dtype in ["int64", "float64"]]
    categorical_cols = [col for col in X.columns if X[col].dtype == "object" ] 
    categorical_cols = [col for col in categorical_cols if col != 'manufacturer']
    
    X_cv, X_val, y_cv, y_val = train_test_split(X,y, test_size = 0.20)
    
    # Preprocessing Numerical data: impute the missing values with the mean and scale the data
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy = "median")),
        ("scaler", StandardScaler())
    ])                    

    # Preprocessing Categorical data: impute the missing values with the most frequent one and onehot encode the categories
    categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ])

    # Combine the two type of column preprocessors
    preprocessor = ColumnTransformer(
            transformers=[
                    ("num", numeric_transformer, numerical_cols),
                    ("cat", categorical_transformer, categorical_cols)
                    ])

    param_grid_forest = { 'predictor__n_estimators': [66,88,100,112,124] } 
    param_grid_ridge  = { 'predictor__alpha': [0.001,0.005,0.01,0.05,0.1,0.5,1,2,5,14.5,15,15.15,24.5,25,25.5] } 
    param_grid_lin  = { 'predictor__n_jobs': [None] } 

    print('====================================')
    print('           By Make                  ')
    print('====================================')    
    print('Starting LinearRegression by Make')
    # LinearRegression by make
    model_name = 'lin_make'
    lin_make_model = GroupbyEstimator('manufacturer', estimator_factory, 'lin',param_grid_lin)
    lin_make_model.fit(X_cv, y_cv) 
    result(lin_make_model, model_name)

    print('Starting RidgeRegression by Make')
    # RidgeRegression by make
    model_name = 'ridge_make'
    ridge_make_model = GroupbyEstimator('manufacturer', estimator_factory, 'ridge',param_grid_ridge)
    ridge_make_model.fit(X_cv, y_cv) 
    result(ridge_make_model, model_name)

    print('Starting RandomForestRegression by Make')
    # RandomForestRegression by make
    model_name = 'forest_make'
    forest_make_model = GroupbyEstimator('manufacturer', estimator_factory, 'forest',param_grid_forest)
    forest_make_model.fit(X_cv, y_cv) 
    result(forest_make_model, model_name)

    print('====================================')
    print('           By State                 ')
    print('====================================')
    categorical_cols = [col for col in X.columns if X[col].dtype == "object" ] 
    categorical_cols = [col for col in categorical_cols if col != 'state']
    # Preprocessing Numerical data: impute the missing values with the mean and scale the data
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy = "median")),
        ("scaler", StandardScaler())
    ])                    

    # Preprocessing Categorical data: impute the missing values with the most frequent one and onehot encode the categories
    categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ])

    # Combine the two type of column preprocessors
    preprocessor = ColumnTransformer(
            transformers=[
                    ("num", numeric_transformer, numerical_cols),
                    ("cat", categorical_transformer, categorical_cols)
                    ])

    print('Starting LinearRegression by State')
    # LinearRegression by state
    model_name = 'lin_state'
    lin_state_model = GroupbyEstimator('state', estimator_factory, 'lin',param_grid_lin)
    lin_state_model.fit(X_cv, y_cv) 
    result(lin_state_model, model_name)

    print('Starting RidgeRegression by State')
    # RidgeRegression by state
    model_name = 'ridge_state'
    ridge_state_model = GroupbyEstimator('state', estimator_factory, 'ridge',param_grid_ridge)
    ridge_state_model.fit(X_cv, y_cv) 
    result(ridge_state_model, model_name)

    print('Starting RandomForestRegression by State')
    # RandomForestRegression by state
    model_name = 'forest_state'
    forest_state_model = GroupbyEstimator('state', estimator_factory, 'forest',param_grid_forest)
    forest_state_model.fit(X_cv, y_cv) 
    result(forest_state_model, model_name)

    print('====================================')
    print('             By All                 ')
    print('====================================')
    categorical_cols = [col for col in X.columns if X[col].dtype == "object" ] 
    # Preprocessing Numerical data: impute the missing values with the mean and scale the data
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy = "median")),
        ("scaler", StandardScaler())
    ])                    

    # Preprocessing Categorical data: impute the missing values with the most frequent one and onehot encode the categories
    categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ])

    # Combine the two type of column preprocessors
    preprocessor = ColumnTransformer(
            transformers=[
                    ("num", numeric_transformer, numerical_cols),
                    ("cat", categorical_transformer, categorical_cols)
                    ])    

    print('Starting LinearRegression by All')
    # LinearRegression on all
    model_name = 'lin_all'
    lin_all_model = estimator_factory('lin',param_grid_lin)
    lin_all_model.fit(X_cv, y_cv) 
    result(lin_all_model, model_name)

    print('Starting RidgeRegression by All')
    # RidgeRegression on all
    model_name = 'ridge_all'
    ridge_all_model = estimator_factory('ridge',param_grid_ridge)
    ridge_all_model.fit(X_cv, y_cv) 
    result(ridge_all_model, model_name)

    print('Starting RandomForestRegression by All')
    # RandomForestRegression on all
    model_name = 'forest_all'
    forest_all_model = estimator_factory('forest',param_grid_forest)
    forest_all_model.fit(X_cv, y_cv) 
    result(forest_all_model, model_name)