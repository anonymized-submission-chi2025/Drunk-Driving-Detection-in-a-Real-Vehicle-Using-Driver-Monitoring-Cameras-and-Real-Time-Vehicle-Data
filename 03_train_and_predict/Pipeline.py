from utils.load_configs import load_configs
from utils.load_data import load_data
from utils.model_training_evaluation import train_LOSO_safely
from utils.pipelines import pipe_lasso
from utils.translate_new_old import translate_new_old
from utils.evaluate import evaluate
import pickle
import numpy as np
from plotting.main_plotting import main_plotting


class Pipeline:
    def __init__(self, config_path=''):
        self.config = load_configs(config_path if config_path != '' else 'main_prediction.yml')

    def change_config(self, updates):
        self.config.update(updates)

    def load_data(self):
        self.data, self.core_features = load_data(config=self.config)

    def train(self):
        self.result_dfs = {}
        self.model_infos = {}

        for model in self.config["models"]:
            if model == "Early Warning":
                y = self.data["y_EW"]
                y_column = "y_EW"
            if model == "Above Limit":
                y = self.data["y_AL"]
                y_column = "y_AL"

            self.model_infos[model] = train_LOSO_safely(
                self.data, pipe_lasso, y_column, self.core_features, model, self.config)

            # The following function is just to interface the plotting function (based on the deprecated results dict).
            self.result_dfs[model] = translate_new_old(
                self.model_infos[model], self.config)

    def evaluate(self):
        self.evaluation_overall = {}
        self.evaluation_scenario = {}

        for key in self.result_dfs:
            if self.config["verbose"]:
                print("Model", key)
            self.evaluation_overall[key] = evaluate(
                self.model_infos[key], self.config)

        for key in self.result_dfs:
            if self.config["verbose"]:
                print("Model per scenario", key)
            self.evaluation_scenario[key] = evaluate(
                self.model_infos[key], self.config, col_analysis_factor='scenarios')

    def plot_results(self):
        if self.config["verbose"]:
            main_plotting(self.result_dfs, self.config)
