import string, random
from datetime import datetime
from bson.objectid import ObjectId


def get_random_string(size=8, chars=(string.ascii_letters + string.digits)):
    return ''.join(random.choice(chars) for _ in range(size))

def get_random_documents(size=3, collection=None):
    documents = collection.aggregate([{ '$sample': { 'size': size } }])
    return [doc for doc in documents]

def start_game(db, identity, n_questions):
    user = db.users.find_one({'username': identity})
    
    random_questions = get_random_documents(size=3, collection=db.mining_the_answers)

    # Start Defining the Game Object Here
    game_key = get_random_string(size=8, chars=(string.ascii_letters + string.digits))
    admin_id = identity
    started_on = datetime.utcnow()
    ended_on = None
    game_name = 'mining_the_answers'
    n_questions = n_questions
    n_players = 1
    status = 2 # waiting
    state = {
        'num': 0,
        'event': 'waiting_to_join'
    }
    users = [
        {
            'username': identity,
            'state': 'waiting'
        }
    ]
    questions = [
        {
            'question': question['question'],
            'true_answer': question['answer'],
            'answers': [],
            'selections': [],
            'scores': []
        } for question in random_questions
    ]
    scores = [
        {
            'user': user['username'],
            'score': 0
        }
    ]

    mining_the_answers = {
        'game_key': game_key,
        'admin_id': admin_id,
        'started_on': started_on,
        'ended_on': ended_on,
        'game_name': game_name,
        'n_questions': n_questions,
        'n_players': n_players,
        'status': status,
        'state': state,
        'users': users,
        'questions': questions,
        'scores': scores
    }
    db.games.insert_one(mining_the_answers)
    return {'msg': 'Started Game', 'game_key': game_key}

def end_game(db, game_key, status=0):
    db.games.update_one({'game_key': game_key}, {'$set': {'status': status, 'ended_on': datetime.utcnow(), 'state': {num: -1, event: 'ended'}}})
    return {'msg': 'Game ended'}

def is_user_playing(db, identity, game_key):
    users = [user['username'] for user in db.games.find_one({'game_key': game_key})['users'] ]
    if identity in users:
        return True
    else:
        return False

def join_game(db, identity, game_key):
    game = db.games.find_one({'game_key': game_key})
    if game['status'] != 2:
        return None
    
    if is_user_playing(db, identity, game_key):
        return {'msg': 'Already joined','game_key': game_key}
    
    user = db.users.find_one({'username': identity})
    user_details = {
        'username': identity,
        'name': user['name'],
        'state': 'waiting'
    }
    
    score_details = {
        'user': user['username'],
        'score': 0
    }
    
    db.games.update_one({'game_key': game_key}, {'$push': {'users': user_details, 'scores': score_details}, '$inc': {'n_players': 1}})
    return {'msg': 'Joined game successfully', 'game_key': game_key}

def enter_game(db, game_key):
    state = {
        'num': 0,
        'event': 'question'
    }
    db.games.update_one({'game_key': game_key}, {'$set': {'status': 1, 'state': state, 'users.$[].state': 'question'}})
    return {'msg': 'Entered game'}

def get_question(db, game_key, qn_num):
    questions = db.games.find_one({'game_key': game_key})['questions']
    if qn_num >= len(questions) or qn_num < 0:
        return None
    question = {
        'question': questions[qn_num]['question'],
        'qn_num': qn_num
    }
    return question

def submit_answer(db, identity, game_key, answer):
    qn_num = answer['qn_num']
    answer = answer['answer']
    
    user = identity
    game_key = game_key
    
    game = db.games.find_one({'game_key': game_key})
    
    def is_answer_submitted():
        answers_array = game['questions'][qn_num]['answers']
        for ans in answers_array:
            if ans['user'] == identity:
                return True
        return False
    
    def is_last_submit():
        total_players = game['n_players']
        answers_count = len(game['questions'][qn_num]['answers'])
        if answers_count == total_players-1:
            return True
        else:
            return False
    
    if is_answer_submitted():
        return {'msg': 'Answer already submitted'}   

    answer = {
        'user': identity,
        'answer': answer
    }
    
    db.games.update_one(filter={'game_key': game_key}, update={'$push': {'questions.{}.answers'.format(qn_num): answer}, '$set': {'users.$[elem].state': 'waiting'}}, array_filters= [{'elem.username': identity}])
    
    if is_last_submit():
        state = {
            'num': qn_num,
            'event': 'selection'
        }
        db.games.update_one({'game_key': game_key}, {'$set': {'state': state, 'users.$[].state': 'selection'}})
        return {'msg': 'Answer submitted at last'}
    
    return {'msg': 'Answer submitted successfully'}

def get_answers(db, game_key, qn_num):
    questions = db.games.find_one({'game_key': game_key})['questions']
    if qn_num >= len(questions) or qn_num < 0:
        return None
    question = questions[qn_num]
    answers = [
        answer for answer in question['answers']
    ]
    
    answers.append({
        'user': 'shoutout_official',
        'answer': question['true_answer']
    })
    return answers

def calculate_midresult(db, game_key, qn_num):
    game = db.games.find_one({'game_key': game_key})
    
    true_answer = game['questions'][qn_num]['true_answer']
    answers = game['questions'][qn_num]['answers']
    selections = game['questions'][qn_num]['selections']
    
    scores = []
    for answer in answers:
        score = {
            'user': answer['user'],
            'psyched': [],
            'result': False,
            'score': 0
        }
        for selection in selections:
            if selection['user'] == answer['user']:
                if selection['answer'] == true_answer:
                    score['result'] = True
                    score['score'] = score['score'] + 1
                continue
                
            if selection['answer'] == answer['answer']:
                score['psyched'].append(selection['user'])
                score['score'] = score['score'] + 1
        scores.append(score)
    state = {}
    if game['state']['num'] + 1 < game['n_questions']:
        state['event'] = 'midresult'
        state['num'] = game['state']['num'] + 1
    db.games.update_one({'game_key': game_key}, {'$set': {'questions.{}.scores'.format(qn_num): scores, 'state': state}})
    
    return {'msg': 'Midresult calculated'}

def calculate_endresult(db, game_key):
    game = db.games.find_one({'game_key': game_key})
    
    questions = game['questions']
    scores = game['scores']
    
    new_scores =  []
    for score in scores:
        user = score['user']
        count = 0
        for question in questions:
            for qn_score in question['scores']:
                if qn_score['user'] == user:
                    count = count + qn_score['score']
                    break
        new_scores.append({
            'user': user,
            'score': count
        })
        
    db.games.update_one({'game_key': game_key}, {'$set': {'scores': new_scores}})
    return None

def submit_selection(db, identity, game_key, selection):    
    qn_num = selection['qn_num']
    answer = selection['answer']
    
    user = identity
    game_key = game_key
    
    game = db.games.find_one({'game_key': game_key})
    
    def is_answer_selected():
        selections_array = game['questions'][qn_num]['selections']
        for selection in selections_array:
            if selection['user'] == identity:
                return True
        return False
    
    def is_last_select():
        total_players = game['n_players']
        selections_count = len(game['questions'][qn_num]['selections'])
        if selections_count == total_players-1:
            return True
        else:
            return False
    
    if is_answer_selected():
        return {'msg': 'Answer already selected'}   

    selection = {
        'user': identity,
        'answer': answer
    }
    if qn_num>=game['n_questions']:
        return {'msg': 'No Question Found'}
    db.games.update_one({'game_key': game_key}, {'$push': {'questions.{}.selections'.format(qn_num): selection}, '$set': {'users.$[elem].state': 'waiting'}}, array_filters= [{'elem.username': identity}])
    
    if is_last_select():
        calculate_midresult(db, game_key, qn_num)
        calculate_endresult(db, game_key)
        state = {
            'num': qn_num,
            'event': 'midresult'
        }
        db.games.update_one({'game_key': game_key}, {'$set': {'state': state, 'users.$[].state': 'midresult'}})
        return {'msg': 'Answer selected at last'}
    
    return {'msg': 'Answer selected successfully'}

def get_midresult(db, game_key, qn_num):
    questions = db.games.find_one({'game_key': game_key})['questions']
    if qn_num >= len(questions) or qn_num < 0:
        return None
    mid_result = questions[qn_num]['scores']
    return mid_result

def get_endresult(db, game_key):
    return db.games.find_one({'game_key': game_key})['scores']

def be_ready(db, game_key, identity):
    game = db.games.find_one({'game_key': game_key})
    def is_already_ready():
        users = game['users']
        for user in users:
            if user['username']==identity and user['state'] == 'waiting':
                return True
        return False
        
    def is_last_to_ready():
        users = game['users']
        for user in users:
            if user['username']!=identity and user['state'] != 'waiting':
                return False
        return True
    
    def is_last_question():
        n_questions = game['n_questions']
        num = game['state']['num']
        
        if num+1 >= n_questions:
            return True
        else:
            return False 
    
    if is_already_ready():
        return {'msg': 'You are already ready'}
    
    if is_last_question():
        end_game(db=db, game_key=game_key, status=0)
        return {'msg': 'Game ended successfully'}
    
    
    if is_last_to_ready():
        num = game['state']['num']
        state = {
            'num': num+1,
            'event': 'question'
        }
        db.games.update_one({'game_key': game_key}, {'$set': {'state': state, 'users.$[].state': 'question'}})
        return {'msg': 'Last to ready'}
    
    db.games.update_one({'game_key': game_key}, {'$set': {'users.$[elem].state': 'waiting'}}, array_filters= [{'elem.username': identity}])
    return {'msg': 'You are ready'}

def get_all_states(db, identity, game_key):
    game = db.games.find_one({'game_key': game_key})
    game_state = game['state']
    users_state = game['users']

    my_state = None
    print(users_state)
    for user in users_state:
        if user['username'] == identity:
            my_state = user
            break

    states = {
        'game_state': game_state,
        'users_state': users_state,
        'my_state': my_state
    }
    return states