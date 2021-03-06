import tweepy,json,datetime,re,random
from langdetect import detect,detect_langs
from time import sleep
from config import *


minim_follower 	= config['minimum_account_follower']
minim_text		= config['minimum_text_after_deleted_keyword']
lang_allowed	= config['language_allowed'] #Indonesia,English,Japan,Korea Utara,Korea Selatan
keys = dict(
	consumer_key=config['consumer_key'],
	consumer_secret=config['consumer_secret'],
	access_token=config['access_token'], 
	access_token_secret=config['access_token_secret']
)

#set api
auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)

black_list_word	= config['blacklist_word']
keyword_match	= config['match_word']
anti_number		= config['anti_number_start_end']
deleted_match	= config['deleted_word']



print("Working Now!\n")

class MyListener(tweepy.StreamListener):

	def write_to_file(self, file,data,mode='a'):
		with open(file, mode) as f:
			f.write(data)
			f.close()


	def on_status(self, status):

		final_data = {
			'id_tweet' : status.id_str,
			'tweet' : status.text,
			'tweet_date' : str(status.created_at),
			'detail_user' : status.user._json,
			'status' : 'normal'
		}


		raw_tweet = final_data['tweet'] #raw tweet can be proccessed (string)
		loc       = final_data['detail_user']['location'] #can be None response careful
		deleted_string 	= re.sub(deleted_match, "", raw_tweet.lower() , re.MULTILINE | re.IGNORECASE)
		detectlang 		= ""

		try:
			detectlang = detect(raw_tweet)

		except Exception as e:

			detectlang = "ep"
			pass

		#jika match dengan keyword Nayeon / Im Nayeon
		if re.search(keyword_match, raw_tweet, re.MULTILINE | re.IGNORECASE):
				
			if final_data['detail_user']['followers_count'] >= minim_follower:

				final_data.update({'status' : 'minim_follower_not_passed'})
				#self.write_to_file(file='my_db.json', data=json.dumps(final_data)+"\n", mode='a')
				

				#Jika tidak ada kata kasar
				if not re.search(black_list_word, raw_tweet, re.MULTILINE | re.IGNORECASE):
					
					if loc is not None:
						
						#ada lokasi
						
						self.write_to_file(file='my_db.json', data=json.dumps(deleted_string)+"\n", mode='a')

						#Jika tweetnya mempunyai panjang yang memenuhi
						if len(deleted_string) > int(minim_text):
							#panjang memenuhi
							
							if detectlang in lang_allowed: #aman bahasanya

								#jika tidak ada nomer di awal atau di akhir
								#10 Nayeon cantik
								#Nayeon cantik 10
								if not re.search(anti_number, raw_tweet,  re.MULTILINE | re.IGNORECASE):

									try:
										api.retweet(final_data['id_tweet'])
										print("*"*30)
										print("After deleted string len is {}".format(len(deleted_string)))
										print("Retweeted tweet id {}".format(final_data['id_tweet']))
										print("*"*30)
										# sleep(random.randint(1,6))
										self.write_to_file(file='id_loged.txt', data=json.dumps({'id':final_data['id_tweet'], 'tweet':raw_tweet})+ "\n", mode='a')
										# self.write
									except tweepy.TweepError as e:
										print(e)
										pass
									except Exception as e:
										print(e)
										pass
								
								else:
									print("%"*30)
									print(deleted_string)
									print("Ada number di awal atau di akhir")
									print("%"*30)
									pass

							else:
								print("#"*30)
								print(raw_tweet)
								print("Tweet tidak berbahasa Indonesia/Inggirs/Korea/Jepang")
								print("Bahasa yang dideteksi [{}]".format(detectlang))
								print("#"*30)
								pass

						else:
							print(raw_tweet, "Tidak cukup panjang!")
							pass

					else:
						print("Tidak ada lokasinya :(")
						pass

				else:
					print("$"*30)
					print(raw_tweet)
					print("Ada kata kata kasar ih :(")
					print("$"*30)
					pass

			else:
				print("Uh sayang Followernya Kurang :( Follower dia {}".format(final_data['detail_user']['followers_count']))
				pass

		else:
			print("-"*30)
			print(raw_tweet)
			print("Gak match sama keyword!")
			print("-"*30)
			pass


	def on_error(self, status_code):
		print(status_code)



Listener = MyListener(api)
Stream = tweepy.Stream(auth=api.auth, listener=Listener)
Stream.filter(track=['Nayeon'])