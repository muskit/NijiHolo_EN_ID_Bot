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
        self.finished_user_timestamps = dict()
        self.ttweets_dict = dict()
        self.good = False # if true, overwrite queue.txt on destruction
        self.__sorted = False

        ## file check, backup copy
        if os.path.exists(self.queue_backup_path):
            print('Found old backup queue! We errored in the previous run.')
            shutil.copyfile(self.queue_backup_path, self.queue_path)
        elif os.path.exists(self.queue_path):
            print('Creating backup queue...')
            shutil.copyfile(self.queue_path, self.queue_backup_path)

        ## initialize structures
        # user timestamps
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
        
        # tweets
        with open(self.queue_path, 'r') as f: # reset seek head
            # Get existing queued TalentTweets
            for line in f:
                tokens = line.split()
                if len(tokens) == 0 or tokens[0][0] == '#':
                    continue
                ttweet = tt.TalentTweet.deserialize(line)
                self.ttweets_dict[ttweet.tweet_id] = ttweet
            print(f'Found {len(self.finished_user_timestamps)} scraped accounts and {len(self.ttweets_dict)} tweets in queue.')

    def add_ttweet(self, ttweet):
        self.__sorted = False
        self.ttweets_dict[ttweet.tweet_id] = ttweet

    def get_ttweet(self, id):
         return self.ttweets_dict[id]
    
    def get_ttweets_dict(self):
        self.__sort_ttweets_dict() if not self.__sorted else None
        return self.ttweets_dict
    
    # overwrite queue.txt
    def save_file(self):
        self.__sort_ttweets_dict()
        with open(self.queue_path, 'w') as f:
            # write timestamps
            for (id, timestamp) in self.finished_user_timestamps.items():
                f.write(f'# {id} {timestamp}\n')
            f.write('\n')
            # write sorted ttweets
            for ttweet in self.ttweets_dict.values():
                f.write(ttweet.serialize() + '\n')
    
    def __sort_ttweets_dict(self):
        self.ttweets_dict = dict(sorted(self.ttweets_dict.items()))
        self.__sorted = True
    
    # destructor
    def __del__(self):
        if self.good:
            print('Ended in good state, deleting backup queue...')
            os.remove(self.queue_backup_path)
        else:
            print('Ended in bad state, keeping backup queue.')