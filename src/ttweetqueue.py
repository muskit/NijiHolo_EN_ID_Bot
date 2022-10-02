# TODO: move queue structures and file handling here
import os
import shutil

import util
import talenttweet as tt

# User timestamps line format:
# # {user_id} {status_num} {UNIX_timestamp}

class TalentTweetQueue:
    instance = None
    
    def __init__(self):
        TalentTweetQueue.instance = self
        self.queue_path = util.get_queue_path()
        self.queue_backup_path = util.get_queue_backup_path()
        self.current_ttweet_path = f'{util.get_project_dir()}/_current_ttweet.txt'
        self.finished_ttweets_path = f'{util.get_project_dir()}/finished_ttweets.txt'
        self.is_good = True
        self.__sorted = False
        self.finished_user_timestamps = dict()
        self.ttweets_dict = dict()
        self.finished_ttweets = list()

        ## file check, backup copy
        if os.path.exists(self.queue_backup_path):
            print('Found backup queue! We errored in the previous run.')
            shutil.copyfile(self.queue_backup_path, self.queue_path)
        elif os.path.exists(self.queue_path):
            print('Creating backup queue...')
            shutil.copyfile(self.queue_path, self.queue_backup_path)

        ## initialize structures
        # user timestamps
        try:
            with open(self.queue_path, 'r') as f:
                for line in f:
                    tokens = line.split()
                    if len(tokens) == 0: continue

                    if tokens[0][0] != '#':
                        print(f'Stopped finding user timestamps at {line}')
                        # reached end of accounts list
                        break
                    if tokens[2] != '-1':
                        self.finished_user_timestamps[int(tokens[1])] = float(tokens[2])
        except: pass
        # ttweets
        try:
            with open(self.queue_path, 'r') as f: # reset seek head
                # Get existing queued TalentTweets
                for line in f:
                    tokens = line.split()
                    if len(tokens) == 0 or tokens[0][0] == '#':
                        continue
                    ttweet = tt.TalentTweet.deserialize(line)
                    self.ttweets_dict[ttweet.tweet_id] = ttweet
                print(f'Found {len(self.finished_user_timestamps)} scraped accounts and {len(self.ttweets_dict)} tweets in queue.')
        except: pass
        # finished ttweets
        try:
            with open(self.finished_ttweets_path, 'r') as f:
                for line in f:
                    self.finished_ttweets.append(int(line))
        except: pass


    def is_empty(self):
        return self.get_count() <= 0

    def add_ttweet(self, ttweet):
        self.__sorted = False
        self.ttweets_dict[ttweet.tweet_id] = ttweet

    def get_ttweet(self, id):
        return self.ttweets_dict[id]

    def get_next_ttweet(self):
        self.is_good = False
        if os.path.exists(self.current_ttweet_path):
            with open(self.current_ttweet_path, 'r') as f:
                return tt.TalentTweet.deserialize(f.readline())

        self.__sort_ttweets_dict()
        key = list(self.ttweets_dict.keys())[0]
        ttweet = self.ttweets_dict.pop(key)
        with open(self.current_ttweet_path, 'w') as f:
            f.write(ttweet.serialize())
        return ttweet
    
    def get_count(self):
        return len(self.ttweets_dict)
    
    ## Call when the TalentTweet retrieved from get_next_ttweet() was
    #  posted successfully.
    def good(self):
        with open(self.current_ttweet_path, 'r') as f:
            ttweet = tt.TalentTweet.deserialize(f.readline())

        self.add_finished_tweet(ttweet.tweet_id)
        os.remove(self.current_ttweet_path)
        self.save_file()
        self.is_good = True
    
    # overwrite queue.txt
    def save_file(self):
        shutil.copyfile(self.queue_path, self.queue_backup_path)
        self.__sort_ttweets_dict()
        with open(self.queue_path, 'w') as f:
            # write timestamps
            for (id, timestamp) in self.finished_user_timestamps.items():
                f.write(f'# {id} {timestamp}\n')

            f.write('\n')

            # write sorted ttweets
            for ttweet in self.ttweets_dict.values():
                f.write(ttweet.serialize() + '\n')

    def add_finished_tweet(self, id):
        self.finished_ttweets.append(id)
        with open(self.finished_ttweets_path, 'a') as f:
            f.write(f'{id}\n')
    
    def __sort_ttweets_dict(self):
        if not self.__sorted:
            self.ttweets_dict = dict(sorted(self.ttweets_dict.items()))
        self.__sorted = True
    
    # destructor
    def __del__(self):
        if self.is_good:
            print('Ended in good state, deleting backup queue...')
            os.remove(self.queue_backup_path)
        else:
            print('Ended in bad state, keeping backup queue.')