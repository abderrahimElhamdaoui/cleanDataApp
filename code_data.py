import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.model_selection import train_test_split,cross_val_score

from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.tree import DecisionTreeRegressor,DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor,KNeighborsClassifier

from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, precision_score, f1_score
import missingno as msno

class press():
    
    def __init__(self,path):
        self.pathData=path
        self.df=pd.read_csv(self.pathData)
        # supermer le id
        self.supId()
        self.typesVariables()
        self.choisirLesVariablesCat()
        self.deleteNoiysValues()
        # print(self.df.columns)
        self.df_num = self.df.select_dtypes(include=[np.number])
        self.non_na_columns = self.df_num.loc[: ,self.df_num.isna().sum() == 0].columns
        self.nan_columns = self.df.loc[: ,self.df.isna().sum() != 0].columns
        self.columns_cat_null=list(set(self.nan_columns)&set(self.cat_variables))
        self.columns_contunue_null=list(self.df_num.loc[: ,self.df_num.isna().sum() != 0].columns)
        # print(self.df_num.columns)
        # print(self.columns_cat_null)
        # print(self.columns_contunue_null)
        self.data_num_netouayer()
        self.data_cat_netouayer()
        # self.data_final()
        
    
    def supId(self):
        self.colonnes_id = [col for col in self.df.columns if 'id' in col.lower()]
        if len(self.colonnes_id)!=0:
            self.df.drop([self.colonnes_id[0]],axis=1,inplace=True)
        # print("supid")
    
    def typesVariables(self):
        self.num_variables = list(self.df.select_dtypes(include=['number']).columns)
        self.cat_variables = list(self.df.select_dtypes(include=['object']).columns)  
        # print("types ariabales")   
        # return num_variables,cat_variables 
    
    def choisirLesVariablesCat(self):
        cat_attributs = []
        nombre_de_lignes = self.df.shape[0]
        for i in self.cat_variables:
            nombre_de_atrbuts=self.df[i].nunique()
        #   choisir les attributs qui ne contient au plus 10% des valeurs déférents.
            if nombre_de_lignes/nombre_de_atrbuts>=(nombre_de_lignes/10):
                cat_attributs.append(i)
        self.cat_variables=cat_attributs

    def deleteNoiysValues(self):
        frequency_counts = self.df.select_dtypes(include=['object']).columns
        for tmp in frequency_counts:
            indexs=list(self.df[tmp].value_counts().index)
            vals=list(self.df[tmp].value_counts())
            q1 = np.percentile(vals, 25)
            q3 = np.percentile(vals, 75)
            Iq=q3-q1
    #         on prend les valeur aberrantes qui associe à les valeurs moins de interquartile.
            va=[i for i in vals if i < Iq]
            for i in va:
                var=indexs[vals.index(i)]
                self.df[tmp]=self.df[tmp].replace(var,None)

    def appliquerRegressorAlgo(self,data,var):
        df_num = data.select_dtypes(include=[np.number])
        X_testeM=df_num.loc[df_num[var].isna() == True, self.non_na_columns]
        df_num=df_num.dropna()
        X = df_num.drop([var], axis=1)
    #   Normalisation : application de StandardScaler
        X_scaled = StandardScaler().fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=X.columns)
        y = df_num[var]
        X_train, X_test, y_train,  y_test = train_test_split(X, y,test_size=0.2,random_state=20)
        algo=self.choisir_RegressorAlgorithme(X_train,y_train, X_test,y_test)
        y_pred = algo.predict(X_testeM)
        data.loc[data[var].isna() == True, var] = y_pred
        return data
    
    def data_num_netouayer(self):
        for col in self.columns_contunue_null:
            self.df=self.appliquerRegressorAlgo(self.df,col)
            
    def appliquerClassifierAlgo(self,data,var):
        df_num = data.select_dtypes(include=[np.number])
        non_na_columns = df_num.loc[: ,df_num.isna().sum() == 0].columns
        X_testvmsmok=data.loc[data[var].isna() == True, non_na_columns]
        df1=data.copy()
        df1=df1.dropna()
        X=df1.select_dtypes(include=[np.number])
        y=df1[var]
        X_scaled = StandardScaler().fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=X.columns)
        X_train, X_test, y_train,  y_test = train_test_split(X, y,test_size=0.2,random_state=20)
        algo=self.choisir_ClassifierAlgorithme(X_train,y_train, X_test,y_test)
        y_pred = algo.predict(X_testvmsmok)
        data.loc[data[var].isna() == True, var] = y_pred
        return data

    # remplacer tous les valeur manquantes des colonnes catégorielles 
    def data_cat_netouayer(self):
        for col in self.columns_cat_null:
            self.df=self.appliquerClassifierAlgo(self.df,col)

    def data_final(self):
        df2=pd.read_csv(self.pathData)
        result=self.df
        if len(self.colonnes_id)!=0:
            result =pd.concat([df2[self.colonnes_id[0]], result], axis=1)
        return result
    
# fonction qui return le bon Regressor Algorithme  
    def choisir_RegressorAlgorithme(self,X_train,y_train, X_test,y_test):  
        knnr = KNeighborsRegressor()
        knnr.fit(X_train, y_train)
        y_pred1 = knnr.predict(X_test)
        knnScor=knnr.score(X_test, y_pred1)
            
        rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_regressor.fit(X_train, y_train)
        y_pred2 = rf_regressor.predict(X_test)
        rf_scor=rf_regressor.score(X_test, y_pred2)
            
        linear_regressor = LinearRegression()
        linear_regressor.fit(X_train, y_train)
        y_pred3 = linear_regressor.predict(X_test)
        lRed_scor=linear_regressor.score(X_test, y_pred3)
            
#         print(knnScor,rf_scor,lRed_scor)
        maxScor=max([knnScor,rf_scor,lRed_scor])
        if maxScor==knnScor:
            return knnr
        if maxScor== rf_scor:
            return rf_regressor
        if maxScor==lRed_scor:
            return linear_regressor
    
    # fonction qui return le bon Classifier Algorithme 
    def choisir_ClassifierAlgorithme(self,X_train,y_train, X_test,y_test):
    #    équilibrage les ciples par Over-sampling à l'aide de RandomOverSampler
        over_sampler = RandomOverSampler(sampling_strategy='auto', random_state=42)
        X_train, y_train = over_sampler.fit_resample(X_train, y_train)
        knnr = KNeighborsClassifier()
        knnr.fit(X_train, y_train)
        y_pred1 = knnr.predict(X_test)
        knnScor=knnr.score(X_test, y_pred1)
        
        rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_classifier.fit(X_train, y_train)
        y_pred2 = rf_classifier.predict(X_test)
        rf_scor=rf_classifier.score(X_test, y_pred2)
        
        lr = LogisticRegression(solver='liblinear')
        lr.fit(X_train, y_train)
        y_pred3 = lr.predict(X_test)
        lr_scor=lr.score(X_test, y_pred3)
        
#         print(knnScor,rf_scor,lr_scor)
        maxScor=max([knnScor,rf_scor,lr_scor])
        if maxScor==knnScor:
            return knnr
        if maxScor== rf_scor:
            return rf_classifier
        if maxScor==lr_scor:
            return lr

# exa=press("datasets/dataset.csv")
# print(exa.data_final())