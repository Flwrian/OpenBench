#!/usr/bin/env python3
import os
import sys
import random
import django
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OpenSite.settings')
django.setup()

from django.contrib.auth.models import User
from OpenBench.models import Test, Machine, Profile, Engine

def get_or_create_user(username):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@example.com'}
    )
    if created:
        user.set_password('password123')
        user.save()
        Profile.objects.get_or_create(user=user)
    return user

def get_or_create_engine(name):
    engine, _ = Engine.objects.get_or_create(
        name=name,
        defaults={
            'source': 'https://github.com/example/engine',
            'sha': '0' * 40,
            'bench': 1234567
        }
    )
    return engine

def generate_results(status, test_mode='SPRT'):
    """Génère des résultats Win/Draw/Loss réalistes"""
    if status == 'active':
        # Test actif avec résultats variés
        games = random.randint(5000, 25000)
        
        # Biais vers les draws (plus réaliste)
        draw_ratio = random.uniform(0.45, 0.65)
        win_loss_ratio = (1.0 - draw_ratio) / 2
        
        # Variation autour du ratio
        win_ratio = win_loss_ratio * random.uniform(0.95, 1.15)
        loss_ratio = 1.0 - draw_ratio - win_ratio
        
        wins = int(games * win_ratio)
        draws = int(games * draw_ratio)
        losses = games - wins - draws
        
    elif status == 'finished_passed':
        # Test réussi (plus de wins que de losses)
        games = random.randint(10000, 40000)
        draw_ratio = random.uniform(0.40, 0.60)
        win_ratio = random.uniform(0.25, 0.35)
        loss_ratio = 1.0 - draw_ratio - win_ratio
        
        wins = int(games * win_ratio)
        draws = int(games * draw_ratio)
        losses = games - wins - draws
        
    elif status == 'finished_failed':
        # Test échoué (plus de losses que de wins)
        games = random.randint(8000, 35000)
        draw_ratio = random.uniform(0.40, 0.60)
        loss_ratio = random.uniform(0.25, 0.35)
        win_ratio = 1.0 - draw_ratio - loss_ratio
        
        wins = int(games * win_ratio)
        draws = int(games * draw_ratio)
        losses = games - wins - draws
        
    elif status in ['awaiting', 'pending']:
        # Pas encore de résultats
        games = wins = draws = losses = 0
    else:
        games = random.randint(100, 2000)
        draw_ratio = random.uniform(0.50, 0.70)
        win_loss_ratio = (1.0 - draw_ratio) / 2
        
        wins = int(games * win_loss_ratio)
        draws = int(games * draw_ratio)
        losses = games - wins - draws
    
    # Génération des pentanomials (approximation)
    if games > 0:
        WW = int(wins * 0.35)
        DW = wins - WW
        LL = int(losses * 0.35)
        LD = losses - LL
        DD = draws
    else:
        WW = DW = LL = LD = DD = 0
    
    return {
        'games': games,
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'WW': WW,
        'DW': DW,
        'DD': DD,
        'LD': LD,
        'LL': LL
    }

def generate_mock_data(num_tests=20):
    """Génère des données de test réalistes"""
    
    print(f"🔧 Génération de {num_tests} tests de démonstration...")
    
    # Utilisateurs
    users = [
        get_or_create_user('magnus'),
        get_or_create_user('hikaru'),
        get_or_create_user('fabiano'),
        get_or_create_user('wesley'),
        get_or_create_user('levon'),
        get_or_create_user('alireza'),
        get_or_create_user('ian')
    ]
    
    # Moteurs
    engines = [
        get_or_create_engine('Stockfish'),
        get_or_create_engine('Ethereal'),
        get_or_create_engine('Berserk'),
        get_or_create_engine('Koivisto'),
        get_or_create_engine('RubiChess'),
        get_or_create_engine('Weiss')
    ]
    
    # Livres d'ouvertures
    books = [
        '8moves_v3.epd',
        'UHO_4060_v2.epd',
        'DFRC.epd',
        'Pohl.epd',
        'UHO_Lichess_4852_v1.epd',
        '4moves_noob.epd'
    ]
    
    # Branches de développement
    dev_branches = [
        'search-v2', 'eval-tuning', 'nnue-update', 'pruning-fix',
        'threads-8', 'endgame-eval', 'mobility-tweak', 'lazy-eval',
        'aspiration-window', 'singular-ext', 'late-move-reduction',
        'futility-pruning', 'null-move', 'pv-search', 'time-management'
    ]
    
    # Contrôles de temps
    time_controls = [
        '8+0.08', '10+0.1', '20+0.2', '40+0.4', '60+0.6', '5+0.05'
    ]
    
    # Statuts possibles
    statuses = ['active', 'finished_passed', 'finished_failed', 'awaiting', 'pending']
    
    test_modes = ['SPRT', 'GAMES', 'SPSA']
    
    created_count = 0
    
    for i in range(num_tests):
        author = random.choice(users)
        engine = random.choice(engines)
        base_engine = random.choice(engines)
        status = random.choice(statuses)
        test_mode = random.choice(test_modes) if status != 'pending' else 'SPRT'
        
        # Génération des résultats
        results = generate_results(status, test_mode)
        
        # Repos
        repos = [
            'https://github.com/official-stockfish/Stockfish',
            'https://github.com/AndyGrant/Ethereal',
            'https://github.com/jhonnold/berserk'
        ]
        
        # Création du test
        test_data = {
            'author': author.username,
            'dev': engine,
            'base': base_engine,
            'dev_repo': random.choice(repos),
            'base_repo': random.choice(repos),
            'dev_engine': engine.name,
            'base_engine': base_engine.name,
            'dev_options': '',
            'base_options': '',
            'dev_time_control': random.choice(time_controls),
            'base_time_control': random.choice(time_controls),
            'book_name': random.choice(books),
            'test_mode': test_mode,
            'priority': random.randint(0, 10),
            'throughput': random.randint(500, 2000),
            'games': results['games'],
            'wins': results['wins'],
            'draws': results['draws'],
            'losses': results['losses'],
            'WW': results['WW'],
            'DW': results['DW'],
            'DD': results['DD'],
            'LD': results['LD'],
            'LL': results['LL'],
            'passed': status == 'finished_passed',
            'failed': status == 'finished_failed',
            'finished': status in ['finished_passed', 'finished_failed'],
            'approved': status not in ['pending', 'awaiting'],
            'awaiting': status == 'awaiting',
            'error': random.random() < 0.05,
            'max_games': 50000 if test_mode == 'GAMES' else 0,
            'elolower': random.uniform(-2.0, 2.0),
            'eloupper': random.uniform(2.0, 6.0),
            'currentllr': random.uniform(-1.0, 2.96) if test_mode == 'SPRT' else 0,
            'lowerllr': -2.94 if test_mode == 'SPRT' else 0,
            'upperllr': 2.94 if test_mode == 'SPRT' else 0,
            'win_adj': 'movecount=3 score=400',
            'draw_adj': 'movenumber=40 movecount=8 score=10',
            'syzygy_adj': 'OPTIONAL',
            'syzygy_wdl': '345',
            'upload_pgns': random.choice(['TRUE', 'FALSE', 'FAILED']),
            'use_penta': True,
        }
        
        # SPSA spécifique
        if test_mode == 'SPSA':
            test_data['spsa'] = {
                'pairs_per': 2,
                'iterations': 100,
                'parameters': {
                    'param1': {'value': 50, 'min': 0, 'max': 100},
                    'param2': {'value': 25, 'min': 0, 'max': 50}
                }
            }
        
        try:
            test = Test.objects.create(**test_data)
            created_count += 1
            
            status_emoji = {
                'active': '🟢',
                'finished_passed': '✅',
                'finished_failed': '❌',
                'awaiting': '⏳',
                'pending': '🕐'
            }
            
            emoji = status_emoji.get(status, '❓')
            print(f"{emoji} Test #{test.id} créé: {author.username} | {engine.name} | "
                  f"{test_data['dev_branch']} | {status} | "
                  f"W:{results['wins']} D:{results['draws']} L:{results['losses']}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du test {i+1}: {e}")
    
    print(f"\n✅ {created_count}/{num_tests} tests créés avec succès!")
    print(f"🌐 Visitez http://localhost:8000/ pour voir les résultats")

def clear_all_tests():
    """Supprime tous les tests existants (pour réinitialisation)"""
    count = Test.objects.count()
    if count > 0:
        response = input(f"⚠️  Voulez-vous supprimer {count} tests existants? (y/N): ")
        if response.lower() == 'y':
            Test.objects.all().delete()
            print(f"🗑️  {count} tests supprimés")
            return True
    return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Génère des données de test pour OpenBench')
    parser.add_argument('-n', '--num', type=int, default=20, help='Nombre de tests à créer')
    parser.add_argument('-c', '--clear', action='store_true', help='Supprimer tous les tests existants')
    parser.add_argument('-f', '--force', action='store_true', help='Force la suppression sans confirmation')
    
    args = parser.parse_args()
    
    if args.clear or args.force:
        if args.force:
            count = Test.objects.count()
            Test.objects.all().delete()
            print(f"🗑️  {count} tests supprimés (force)")
        else:
            clear_all_tests()
    
    generate_mock_data(args.num)
