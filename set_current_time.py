#!/usr/bin/env python
#-*- encoding: utf8 -*-
"""
{
  "year": 2024,
  "month": 1,
  "day": 19,
  "hour": 23,
  "minute": 54,
  "seconds": 6,
  "milliSeconds": 422,
  "dateTime": "2024-01-19T23:54:06.4228987",
  "date": "01/19/2024",
  "time": "23:54",
  "timeZone": "Europe/Berlin",
  "dayOfWeek": "Friday",
  "dstActive": false
}

Link: https://www.timeapi.io/swagger/index.html
"""
import os
import json
import time
from datetime import datetime, timedelta

import requests


class DateCounter:
	""" Programme de contage de date """

	def __init__(self):
		self._storage_file = '.sct'
		self._date = datetime(day=1, month=1, year=2024)
		self._start = True

	def load_file(self):
		""" Chargement des donnees depuis un fichier existant """
		if os.path.isfile(self._storage_file):
			with open(self._storage_file, mode='r') as sf:
				dd = int(sf.readline().strip())
				mm = int(sf.readline().strip())
				yy = int(sf.readline().strip())
				self._date = datetime(day=dd, month=mm, year=yy)

	def get_next_date(self) -> datetime:
		if not self._start:
			self._date = self._date + timedelta(days=1)
		else:
			self._start = False

		return self._date

	def current_date(self):
		""" Recupere la date et l'heure actuelle """
		self._date = datetime.now()

	def update_file(self):
		""" Sauvegarde des nouvelle donnees dans le fichier """
		with open(self._storage_file, mode='w') as sf:
			sf.write(str(self._date.day) + '\n')
			sf.write(str(self._date.month) + '\n')
			sf.write(str(self._date.year) + '\n')


def set_date(dd: int, mm: int, yy: int):
	""" execution de la commande pour regler date du systeme """
	os.system((
		f'sudo date '
		f'--set="{mm:02d}/{dd:02d}/{yy}"'
	))


def main():
	""" Fonction principale """
	URL = 'https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Berlin'
	date_counter = DateCounter()
	n_retries = 100
	retries_counter = 0

	date_counter.load_file()
	while retries_counter < n_retries:
		try:
			print(f"{'INFO':4s} Getting data from {URL} ...")
			response = requests.get(url=URL, headers={'accept':'application/json'})
			data = response.json()
			print(json.dumps(data, indent=4))

			# recuperation de l'heure
			hour = data['hour']
			tag = 'AM'
			if hour > 12:
				tag = 'PM'
				hour = hour % 12

			date = data['date']
			minute = data['minute']
			seconds = data['seconds']

			# execution de la commande pour regler l'heure du systeme
			os.system((
				f'sudo date '
				f'--set="{date} {hour:02d}:{minute:02d}:{seconds:02d} {tag}"'
			))

			date_counter.update_file()
			break
		except requests.exceptions.ConnectionError as error:
			retries_counter += 1
			err_message = str(error)

			if "NewConnectionError" in err_message:
				print(f"{'ERRO':4s} \033[91mNo connection found!\033[0m {error}")
				break
			elif "SSLCertVerificationError" in err_message:
				print(f"{'INFO':4s} Retry to update datetime for {retries_counter}")

				next_date = date_counter.get_next_date()
				set_date(next_date.day, next_date.month, next_date.year)
				time.sleep(1)


if __name__ == '__main__':
	main()
