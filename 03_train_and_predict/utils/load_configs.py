#####################################################################
# Copyright (C) 2024 HIDDEN UNIVERSITY
# HIDDEN WEBSITE
# HIDDEN SUBTEXT
# HIDDEN INSTITUTE
# 
# Authors: AUTHORS CURRENTLY HIDDEN DUE TO ONGOING PEER REVIEW PROCESS
# 
# Licensed under the MIT License (the "License");
# you may only use this file in compliance with the License.
# You may obtain a copy of the License at
# 
#         https://mit-license.org/
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
####################################################################

import yaml
import os


def load_configs(config_file: str) -> dict[str, any]:
    with open(config_file, 'r') as yamlfile:
        cfg_prediction = yaml.load(yamlfile, Loader=yaml.FullLoader)

    # Read in processing configs
    config = {}
    config["data_directory"] = cfg_prediction["data_directory"]
    config["use_parallel_processing"] = cfg_prediction['use_parallel_processing']
    config["use_on_top_model"] = cfg_prediction["use_on_top_model"]
    config["verbose"] = cfg_prediction['verbose']
    config["only_load_core_features"] = cfg_prediction["only_load_core_features"]
    config["dmc_features"] = cfg_prediction['dmc_features']
    config["can_features"] = cfg_prediction['can_features']
    config["window_length"] = cfg_prediction['window_length']
    config["num_cores"] = cfg_prediction['num_cores']
    config["use_dmc"] = cfg_prediction['use_dmc']
    config["use_can"] = cfg_prediction['use_can']
    config["use_placebo"] = cfg_prediction['use_placebo']
    config["use_reference"] = cfg_prediction['use_reference']
    config["models"] = cfg_prediction['models']

    treatment_participants = cfg_prediction['treatment_participants']
    placebo_participants = cfg_prediction['placebo_participants']
    reference_participants = cfg_prediction['reference_participants']
    selected_participants = {"treatment": treatment_participants,
                             "reference": reference_participants,
                             "placebo": placebo_participants}
    config["selected_participants"] = selected_participants

    return config
