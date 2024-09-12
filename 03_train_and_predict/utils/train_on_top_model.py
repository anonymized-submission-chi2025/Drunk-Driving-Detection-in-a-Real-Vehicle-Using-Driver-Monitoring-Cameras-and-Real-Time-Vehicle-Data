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

import pandas as pd
import numpy as np
from collections import Counter
import warnings

def drives_segmentation(y_train: pd.Series, y_test: pd.Series, 
                        y_proba_train: pd.Series, y_proba_test: pd.Series,
                        ids_train: pd.Series, ids_test: pd.Series,
                        scenarios_train: pd.Series, scenarios_test: pd.Series,
                        states_train:pd.Series, states_test: pd.Series
                       ) -> tuple[dict[tuple[str, str, int], pd.Series], 
                                  dict[tuple[str, str, int], pd.Series]]:
    
    df_test = pd.DataFrame({'y_test': y_test,
                            'y_proba_test': y_proba_test,
                            'ids_test': ids_test,
                            'scenarios_test': scenarios_test,
                            'states_test': states_test})
    
    # Group by the unique combinations of ids, scenarios, phases.
    grouped_test = df_test.groupby(['ids_test', 'scenarios_test',
                                    'states_test'])
    
    # Split the series according to these groups.
    split_proba_test = {name: group['y_proba_test'] for name, group in 
                        grouped_test}
    split_y_test = {name: group['y_test'] for name, group in grouped_test}
    
    # Ensure the sequences are in the original order.
    ordered_keys_test = (df_test[['ids_test', 'scenarios_test', 'states_test']]
                    .drop_duplicates().to_records(index=False))
    ordered_split_proba_test = {tuple(key): split_proba_test[tuple(key)] for 
                                key in ordered_keys_test}
    ordered_split_y_test = {tuple(key): split_y_test[tuple(key)] for key in 
                            ordered_keys_test}

    df_train = pd.DataFrame({'y_train': y_train, 
                            'y_proba_train': y_proba_train,
                            'ids_train': ids_train,
                            'scenarios_train': scenarios_train,
                            'states_train': states_train})
    
    # Group by the unique combinations of ids, scenarios, phases.
    grouped_train = df_train.groupby(['ids_train', 'scenarios_train',
                                    'states_train'])
    
    # Split the series according to these groups.
    split_proba_train = {name: group['y_proba_train'] for name, group in
                         grouped_train}
    split_y_train = {name: group['y_train'] for name, group in grouped_train}

    # Ensure the sequences are in the original order.
    ordered_keys_train = (df_train[['ids_train', 'scenarios_train', 'states_train']]
                    .drop_duplicates().to_records(index=False))
    ordered_split_proba_train = {tuple(key): split_proba_train[tuple(key)] for
                                 key in ordered_keys_train}
    ordered_split_y_train = {tuple(key): split_y_train[tuple(key)] for key in
                             ordered_keys_train}

    return ordered_split_y_train, ordered_split_y_test, \
        ordered_split_proba_train, ordered_split_proba_test

def progressive_moving_average_filter(y_proba_test: pd.Series, sequences_test:
                                      dict[tuple[str, str, int], pd.Series]
                                     ) -> pd.Series:

    y_proba_test_smoothed = y_proba_test.copy()
    y_proba_test_smoothed[:] = -1
    
    for key, sequence in sequences_test.items():
        # progressive_avg = sequence.expanding().mean()
        progressive_avg = sequence.rolling(window='180s', min_periods=1).mean()
        for datetime in progressive_avg.index:
            y_proba_test_smoothed.loc[datetime] = progressive_avg.loc[datetime]
        
    return y_proba_test_smoothed
'''
def hidden_markov_model(y_sequences_train: dict[tuple[str, str, int], 
                        pd.Series], y_proba_sequences_train: 
                        dict[tuple[str, str, int], pd.Series], 
                        y_proba_sequences_test: dict[tuple[str, str, int],
                        pd.Series]) -> pd.Series:
   
    ground_truth_train_sequences = [series for series in y_sequences_train.values()]
    
    train_probability_sequences = [series for series in y_proba_sequences_train.values()]
    train_observed_sequences = [seq.apply(lambda x: 1 if x > 0.5 else 0) for seq in train_probability_sequences]
    
    test_probability_sequences = [series for series in y_proba_sequences_test.values()]
   
    # Convert test probabilities to observed states: 0 (not drunk) and 1 (drunk)
    test_observed_sequences = [seq.apply(lambda x: 1 if x > 0.5 else 0) for seq in test_probability_sequences]
    
    # Estimate transition and emission probabilities using training data
    n_states = 2  # Not drunk, Drunk
      
    # Initial state probabilities (example, can be uniform or estimated from data)
    initial_state_probabilities = np.array([0.5, 0.5])
  
    # Create the HMM model
    hmm_model = hmm.MultinomialHMM(n_components=n_states)
    hmm_model.n_features = n_observations
    # hmm_model = hmm.MultinomialHMM(n_components=n_states)

    # Set the initial parameters
    emission_probabilities = np.array([
        [0.8, 0.2],  # If not drunk, high probability of predicting not drunk
        [0.2, 0.8]   # If drunk, high probability of predicting drunk
    ])

    hmm_model.emissionprob_ = emission_probabilities
    
    # Fit the model on the training observation sequence
    all_train_observations = pd.concat(train_observed_sequences).values.reshape(-1, 1)
    sequence_lengths = [len(seq) for seq in train_observed_sequences]
    # hmm_model.fit(all_train_observations, lengths=sequence_lengths)
    hmm_model.fit(all_train_observations[0].reshape(-1,1))

    transition_probabilities = np.array([
        [0.95, 0.05],  # Not drunk state
        [0.05, 0.95]   # Drunk state
    ])

    emission_probabilities = np.array([
        [0.8, 0.2],  # If not drunk, high probability of predicting not drunk
        [0.2, 0.8]   # If drunk, high probability of predicting drunk
    ])
    initial_state_probabilities = np.array([0.5, 0.5])

    hmm_model.startprob_ = initial_state_probabilities
    hmm_model.transmat_ = transition_probabilities
    hmm_model.emissionprob_ = emission_probabilities

    # Function to predict probabilities for test sequences
    def predict_probabilities(hmm_model, test_sequence):
        n_timesteps = len(test_sequence)  
        test_sequence = test_sequence.astype(int)
        test_sequence = test_sequence.values.reshape(-1, 1)
        forward_probabilities = hmm_model.predict_proba(test_sequence)
        posterior_probabilities = forward_probabilities[-1] / forward_probabilities[-1].sum()
        return posterior_probabilities
    
    # Apply the model to test sequences
    predicted_probabilities_all = pd.Series(dtype='float64')
    for test_prob_seq in test_probability_sequences:
        test_obs_seq = test_prob_seq.apply(lambda x: 1 if x > 0.5 else 0)
        predicted_probabilities = [0.5, 0.5,]
        for t in range(3, len(test_obs_seq) + 1): #used to be one
            past_obs_seq = test_obs_seq[:t]
            posterior_probs = predict_probabilities(hmm_model, past_obs_seq)
            predicted_probabilities.append(posterior_probs[1])  # Probability of being drunk (state 1)
       
        predicted_probabilities = pd.Series(predicted_probabilities, index = test_prob_seq.index)
        predicted_probabilities_all = pd.concat([predicted_probabilities_all, predicted_probabilities])
        
    return predicted_probabilities_all
'''

def train_on_top_model(y_proba_train: np.array, y_proba_test: np.array,
                       y_train: pd.Series, y_test: pd.Series, 
                       ids_train: pd.Series, ids_test: pd.Series,
                       scenarios_train: pd.Series, scenarios_test: pd.Series,
                       states_train:pd.Series, states_test: pd.Series) -> None:

    warnings.warn("The on-top-models are work in progress and not rigorously tested")

    y_proba_test = pd.Series(y_proba_test, index=y_test.index)
    y_proba_train = pd.Series(y_proba_train, index=y_train.index)

    if len(states_train.unique()) != 3:
        raise ValueError("The number of state is unequal to 3")

    y_sequences_train, y_sequences_test, y_proba_sequences_train, \
        y_proba_sequences_test = drives_segmentation(y_train, y_test,
                                                     y_proba_train,
                                                     y_proba_test, ids_train,
                                                     ids_test, scenarios_train,
                                                     scenarios_test, 
                                                     states_train, states_test)
    
    y_proba_test_smoothed = progressive_moving_average_filter(y_proba_test, 
                                                              y_proba_sequences_test)
    '''
    y_proba_test_smoothed = hidden_markov_model(y_sequences_train, y_proba_sequences_train, 
                        y_proba_sequences_test)
    '''
    # print(y_test.size)
    
    
    return y_proba_test_smoothed