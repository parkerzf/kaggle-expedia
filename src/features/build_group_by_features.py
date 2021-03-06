import numpy as np
import pandas as pd
import sys
import os
from sklearn.externals import joblib

scriptpath = os.path.dirname(os.path.realpath(sys.argv[0])) + '/../'
sys.path.append(os.path.abspath(scriptpath))
import utils



def hotel_clusters_to_ranking_features(row):
	"""
    Transform a top 5 hotel clusters to a length 100 ranking features
    :param row: the instance row
    :return: the length 100 ranking features
	"""
	ranking_features = np.empty(100)
	ranking_features.fill(100)
	ranking = [1, 2, 3, 4, 5]
	ranking_features[map(int, row[1].split())] = ranking
	return pd.Series(ranking_features)


def gen_top_k_hotel_cluster(dataset, group_by_field, type = 'test'):
	"""
	Generate the top k hotel clusters for the dataset w.r.t. the group_by_field
	:param dataset: train/test dataset
	:param group_by_field: group by field to get the related group by model 
	:param type: train/test 
	:return: the dataframe with the top k hotel clusters
	"""
	group_by_model = joblib.load(utils.model_path + 
		'_'.join(['top', str(utils.k), 'cw', str(utils.click_weight), 'group', group_by_field, 'year', utils.train_year]) + '.pkl')
	merged_df = dataset.merge(group_by_model, how='left',left_on= group_by_field, right_index=True)
	merged_df.reset_index(inplace = True)

	if type == 'test':
		result = merged_df[['index', 'hotel_cluster']]
		result.columns =  ['id', 'hotel_cluster']
	elif type == 'train':
		result = merged_df[['index', 'hotel_cluster_y']]
		result.columns =  ['id', 'hotel_cluster']

	return result


#############################################################
####################   train dataset     ####################
#############################################################
train = utils.load_train('group_by')
train_is_booking = train[train.is_booking == 1]
train_is_booking.reset_index(inplace = True)
del train

print 'generate top k hotel clusters with orig_destination_distance model...'
result = gen_top_k_hotel_cluster(train_is_booking, 'orig_destination_distance', 'train')
print 'generate top k hotel clusters with srch_destination_id model...'
result = utils.fill_all_top_5(train_is_booking, result, 'srch_destination_id', 'train')
print 'generate top k hotel clusters with user_id model...'
result = utils.fill_all_top_5(train_is_booking, result, 'user_id', 'train')
print 'generate top k hotel clusters with hotel_market model...'
result = utils.fill_all_top_5(train_is_booking, result, 'hotel_market', 'train')
print 'hotel clusters to ranking features...'
new_result = result.apply(lambda row: hotel_clusters_to_ranking_features(row), axis=1)
new_result.columns = ['_'.join(['hotel_cluster', str(hotel_cluster_id), 'rank']) for hotel_cluster_id in range(100)]
new_result = pd.concat([train_is_booking['date_time'], new_result], axis=1)

new_result.to_csv(utils.processed_data_path +
	'_'.join(['train_is_booking_group_by', 'top', str(utils.k), 'cw', str(utils.click_weight), 'year', utils.train_year]) +
	'.csv', header=True, index=False)

del train_is_booking

#############################################################
####################   test dataset      ####################
#############################################################
test  = utils.load_test('group_by')

print 'generate top k hotel clusters with orig_destination_distance model...'
result = gen_top_k_hotel_cluster(test, 'orig_destination_distance')
print 'generate top k hotel clusters with srch_destination_id model...'
result = utils.fill_all_top_5(test, result, 'srch_destination_id')
print 'generate top k hotel clusters with user_id model...'
result = utils.fill_all_top_5(test, result, 'user_id')
print 'generate top k hotel clusters with hotel_market model...'
result = utils.fill_all_top_5(test, result, 'hotel_market')
print 'hotel clusters to ranking features...'
new_result = result.apply(lambda row: hotel_clusters_to_ranking_features(row), axis=1)
new_result.columns = ['_'.join(['hotel_cluster', str(hotel_cluster_id), 'rank']) for hotel_cluster_id in range(100)]

new_result.to_csv(utils.processed_data_path +
	'_'.join(['test_groupb_by', 'top', str(utils.k), 'cw', str(utils.click_weight), 'year', utils.train_year]) +
	'.csv', header=True, index_label='id')




