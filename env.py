import matplotlib.pyplot as plt
import numpy as np
import math
import random
import os, csv

class system_model:
	def __init__(self):
		self.nMBS = 1
		self.nSBS = 3
		self.rMBS = 1000  # in m
		self.dmin = 800
		self.nUE = 5  # 8 # or K
		self.P_Max_MBS = 10 ** (4.3 - 3)  # in 19.95 W
		self.P_Max_SBS = 10 ** (2.4 - 3)  # in 0.25 W
		self.Pc_MBS = 130  # in W
		self.Pc_SBS = 0.5  # 6.8# in W
		self.tx_pw_MBS = 50  #dbm
		self.tx_pw_SBS = 35 #dbm
		self.Noise = -174   #dbm    #(10 ** (-17.4)) * 0.001  # W/Hz
		self.SINR_threshold = 1  # 0dB / 1dB / 2dB



		self.datarate_demand = [random.randrange(1, 200) for i in range(self.nUE)]
		self.delay = [[random.randrange(1, 100) for i in range(self.nUE)]]
		self.UESL_coeff = 1024
		self.UE_SL = [i/self.UESL_coeff for i in self.datarate_demand]
		print('Individual user load', self.UE_SL)

		SBS_R, SBS_A = np.random.uniform(
			self.dmin, self.rMBS, self.nSBS), np.random.uniform(0, 2 * math.pi, self.nSBS)
		self.xSBS, self.ySBS = [r * math.cos(a) for r, a in zip(SBS_R, SBS_A)], [
			r * math.sin(a) for r, a in zip(SBS_R, SBS_A)]



		UE_R, UE_A = np.random.uniform(
			self.dmin, self.rMBS, self.nUE), np.random.uniform(0, 2 * math.pi, self.nUE)
		self.xUE, self.yUE = [r * math.cos(a) for r, a in zip(UE_R, UE_A)], [r * math.sin(a) for r, a in zip(UE_R, UE_A)]


		self.UE2SBS_dist = [[0]*self.nSBS for _ in range(self.nUE)]




		for i, (X, Y) in enumerate(zip(self.xSBS, self.ySBS)):
			for user in range(self.nUE):
				self.UE2SBS_dist[user][i] = math.pow((X - self.xUE[user]), 2) + math.pow((Y - self.yUE[user]), 2)
		print(self.UE2SBS_dist)

		self.user_association_vector = np.argmin(self.UE2SBS_dist, axis=1) + 1

		print(self.user_association_vector)

		self.user_association = {new_list + 1 : [] for new_list in range(self.nSBS)}

		for x in range(len(self.user_association_vector)):
			self.user_association[self.user_association_vector[x]].append(x+1)
		print('Initial user association', self.user_association)

		self.systemload = [0]*self.nSBS

		for x in self.user_association:
			for y in self.user_association[x]:
				self.systemload[x-1] += self.UE_SL[y-1]
		print('system load', self.systemload)







		#path loss
		self.dSBS2UE = [((self.xUE - x) ** 2 + (self.yUE - y) ** 2) **
		                0.5 for x, y in zip(self.xSBS, self.ySBS)]
		self.dMBS2SBS = [((x) ** 2 + (y) ** 2) ** 0.5 for x,
		                                                  y in zip(self.xSBS, self.ySBS)]




	def plotNetwork(self, name):
		# 1)plot TP & UE
		plt.figure(figsize=(5, 5))
		plt.scatter([0], [0], s=80, c='green',
		            marker='o', alpha=0.5, label='MBS')
		plt.scatter(self.xSBS, self.ySBS, s=50, c='blue',
		            marker='D', alpha=0.5, label='SBS')
		plt.scatter(self.xUE, self.yUE, s=50, c='red',
		            marker='*', alpha=0.5, label='UE')
		# 2)Display index
		plt.annotate("0", xy=(0, 0), xytext=(0, 0))
		cnt = 1
		for x, y in zip(self.xSBS, self.ySBS):
			plt.annotate("%s" % cnt, xy=(x, y), xytext=(x, y))
			cnt = cnt + 1
		cnt = 1
		for x, y in zip(self.xUE, self.yUE):
			plt.annotate("%s" % cnt, xy=(x, y), xytext=(x, y))
			cnt = cnt + 1
		margin = 50
		plt.xlim((-self.rMBS - margin, self.rMBS + margin))
		plt.ylim((-self.rMBS - margin, self.rMBS + margin))
		plt.title('Network Geometry ')
		plt.xlabel('Distance(m)')
		plt.ylabel('Distance(m)')
		plt.legend(loc='upper right')
		plt.savefig(name + '.png')
		plt.show()

	def _SINR(self, I, P):
		G_UE = [self.G[self.chosen_UE2TP[i], i] for i in range(self.nUE)]
		# np.clip(np.array(G_UE)*np.array(P)/(self.Noise*self.subB+np.array(I)),-self.delta_max,self.delta_max)
		SINR = np.array(G_UE) * np.array(P) / (self.Noise * self.subB + np.array(I))
		# signal_part=np.array(G_UE)*np.array(P)
		return SINR

	def readCSV(self, FileName):
		# self.ori_TP2UE = {i: [] for i in range(self.ori_sizeTable)}
		# self.ori_UE2TP = {}

		with open(FileName + '.csv', newline='') as csvfile:
			rows = csv.reader(csvfile)
			rows = list(rows)
			# read SBS, UE location
			self.xSBS, self.ySBS = [float(i) for i in rows[0]], [
				float(i) for i in rows[1]]
			self.xUE, self.yUE = [float(i) for i in rows[2]], [
				float(i) for i in rows[3]]
			# read channel gain
			self.G = np.array([float(i) for lis in rows[4:4 + self.nSBS]
			                   for i in lis]).reshape(self.nSBS, self.nUE)
			print('Channel gain', self.G)

			self.SINR = [[0]*self.nUE for _ in range(self.nSBS)]


			for i in range(self.nSBS):
				for user in range(self.nUE):
					self.SINR[i][user] = (self.G[i][user]* self.tx_pw_SBS)
					den = 0
					for sb in range(self.nSBS):
						if sb != i:
							den += self.G[sb][user] * self.systemload[sb]
					den = (den * self.tx_pw_SBS) + self.Noise
					self.SINR[i][user] = self.SINR[i][user]/den

			print('SINR', self.SINR)





if __name__ == '__main__':
	env = system_model()
	env.plotNetwork('plots')
	scenario_name = 'EnvInfo_3'
	env.readCSV(FileName=scenario_name)
