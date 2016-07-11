import json 
import datetime
import sys
import numpy as np

# extract information of time, target, actor from Venmo trasaction data 
def extract_info(json_input):
	payment = json.loads(json_input)
	created_time = datetime.datetime.strptime(payment['created_time'],'%Y-%m-%dT%H:%M:%SZ')
	target = payment['target']
	actor = payment['actor']
	return created_time, target, actor

#remove old payments in the graph 
def remove_edge(graph,created_time):
	for node in graph:
		for neighbour_node in graph[node]:
			if graph[node][neighbour_node]<created_time-datetime.timedelta(seconds=60):
				del graph[node][neighbour_node]
	return graph

# update edges if created_time is within 60 secconds time window 
def update_edge(graph,created_time,target,actor):
	if target in graph and actor in graph:
		if actor in graph[target]:
			if graph[target][actor] < created_time:
				graph[target][actor] = created_time
				graph[actor][target] = created_time
		else:
			graph[actor][target] = created_time
			graph[target][actor] = created_time
	elif target in graph and actor not in graph:
		graph[target][actor] = created_time
		graph[actor] = {target:created_time}
	elif actor in graph and target not in graph:
		graph[actor][target]=created_time
		graph[target]={actor:created_time}
	else:
		graph[target] = {actor:created_time}
		graph[actor] = {target:created_time}
	return graph

# remove nodes with no connection
def remove_node(graph):
	for node in graph:
		if len(graph[node])==0:
			del graph[node]
	return graph

# update the maxinum timestamp and mininum time stamp
def update_timestamp(graph,mininum_timestamp,maxinum_timestamp):
	for node in graph:
		for neighbour_node in graph[node]:
			if graph[node][neighbour_node] > maxinum_timestamp:
				maxinum_timestamp = graph[node][neighbour_node]
			elif graph[node][neighbour_node] < mininum_timestamp:
				mininum_timestamp = graph[node][neighbour_node]
			else:
				pass
	return mininum_timestamp,maxinum_timestamp

# calculate the median degree 
def cal_degree(graph):
	degree_list = []
	for node in graph:
		degree = len(graph[node])
		degree_list.append(degree)
	median_degree = np.median(degree_list)
	return '{:.2f}'.format(median_degree)

def main(input_file_name,output_file_name):
	graph = {}
	output = []
	maxinum_timestamp = datetime.datetime.min + datetime.timedelta(seconds=60)
	mininum_timestamp = datetime.datetime.max - datetime.timedelta(seconds=60)

	with open(input_file_name) as venmo_input:
		for line in venmo_input:
			print graph
			created_time, target, actor = extract_info(line)
			# make sure there is no missing values for actors 
			if actor != None:
				# the new payment falls into the 60 seconds time window 
				if created_time <= (mininum_timestamp + datetime.timedelta(seconds=60)) or created_time >= (maxinum_timestamp - datetime.timedelta(seconds=60)):
					graph = update_edge(graph,created_time,target,actor)
					median_degree = cal_degree(graph)
				# the new payment falss beyond the 60 seconds time window 
				elif created_time > (mininum_timestamp + datetime.timedelta(seconds=60)):
					graph = remove_edge(graph,created_time)
					graph = remove_node(graph)
					median_degree = cal_degree(graph)
				# the new pyament arrvies out of time  
				else:
					median_degree = output[-1]
			mininum_timestamp, maxinum_timestamp = update_timestamp(graph, mininum_timestamp, maxinum_timestamp)
			output.append(median_degree)

	# generate the output list as a text file 
	with open(output_file_name,'w') as venmo_output:
		venmo_output.write("\n".join(map(lambda x: x, output)))

if __name__ == '__main__':
	main(sys.argv[1],sys.argv[2])