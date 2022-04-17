import heapq
from env import system_model

def solution(user_association, user_info, sbs_info, SL_low_thres, SL_high_thres): #user_info -- [load, index, type(data/delay)], sbs_info -- [SL, index]
	pq1 = []
	pq2 = []

	macro_info = {0: []}

	heapq.heapify(pq1)
	heapq.heapify(pq2)

	for item in sbs_info:
		if item[0] < SL_low_thres:
			# offloading to macro base stations from the SBS in off mode
			for user in user_association[item[1]]:
				macro_info[0] += user
			sbs_info.pop(item)      # turn off the SBS

	# associate user with the remaining SBS

	for item in sbs_info:
		if item[0] >= SL_high_thres:
			heapq.heappush(pq1, [-1*item[0], item[1]])
		else:
			heapq.heappush(pq2, item)

	while len(pq1) == 0:
		tmp = heapq.heappop(pq1)
		tmp1 = heapq.heappop(user_association[tmp[1]])
		tmp[0] = (-1 * tmp[0]) - tmp1[0]
		tmp[0] = -1*tmp[0]

		tmp2 = heapq.heappop(pq2)
		tmp2[0] += tmp1[0]
		heapq.heappush(user_association[tmp2[1]], tmp1)


		if tmp[0] >= SL_high_thres:
			heapq.heappush(pq1, tmp)
		else:
			heapq.heappush(pq2, tmp)

		if tmp2[0] >= SL_high_thres:
			break
		heapq.heappush(pq2, tmp2)


	print('Ultimate user association', user_association)













if __name__ == '__main__':
	model = system_model()
	user_association = model.user_association()
