#!/usr/bin/env python3
# Script pour créer des tests de démonstration avec différents statuts

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OpenSite.settings')
django.setup()

from OpenBench.models import Engine, Test
from django.contrib.auth.models import User

def create_demo_tests():
    """Crée des tests de démonstration avec différents statuts"""
    
    # Trouver ou créer un utilisateur de test
    user, _ = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@example.com'}
    )
    
    # Créer ou récupérer des engines de test
    dev_engine, _ = Engine.objects.get_or_create(
        name='Stockfish',
        sha='abc123',
        bench=5000000
    )
    
    base_engine, _ = Engine.objects.get_or_create(
        name='Stockfish',
        sha='def456',
        bench=4950000
    )
    
    # Configuration des tests avec différents statuts
    test_configs = [
        {
            'author': 'Magnus',
            'dev_branch': 'master',
            'base_branch': 'master',
            'status': 'pending',
            'test_mode': 'SPRT',
            'dev_time_control': '10+0.1',
            'book': 'UHO_4060_v2.epd',
            'games': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
        },
        {
            'author': 'Hikaru',
            'dev_branch': 'search-v2',
            'base_branch': 'master',
            'status': 'awaiting',
            'test_mode': 'SPRT',
            'dev_time_control': '60+0.6',
            'book': '8moves_v3.epd',
            'games': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
        },
        {
            'author': 'Fabiano',
            'dev_branch': 'eval-tuning',
            'base_branch': 'dev',
            'status': 'active',
            'test_mode': 'SPRT',
            'dev_time_control': '20+0.2',
            'book': 'UHO_4060_v2.epd',
            'games': 15420,
            'wins': 3150,
            'draws': 9180,
            'losses': 3090,
            'WW': 850,
            'DW': 1450,
            'DD': 6280,
            'LD': 1450,
            'LL': 820,
        },
        {
            'author': 'Wesley',
            'dev_branch': 'nnue-update',
            'base_branch': 'master',
            'status': 'active',
            'test_mode': 'GAMES',
            'dev_time_control': '8+0.08',
            'book': 'Pohl.epd',
            'games': 8240,
            'wins': 2100,
            'draws': 4050,
            'losses': 2090,
            'WW': 650,
            'DW': 800,
            'DD': 2450,
            'LD': 800,
            'LL': 640,
            'max_games': 10000,
        },
        {
            'author': 'Alireza',
            'dev_branch': 'pruning-fix',
            'base_branch': 'dev',
            'status': 'finished_passed',
            'test_mode': 'SPRT',
            'dev_time_control': '40+0.4',
            'book': 'DFRC.epd',
            'games': 28640,
            'wins': 7250,
            'draws': 14180,
            'losses': 7210,
            'WW': 2150,
            'DW': 2950,
            'DD': 8280,
            'LD': 2950,
            'LL': 2060,
        },
        {
            'author': 'Levon',
            'dev_branch': 'threads-8',
            'base_branch': 'master',
            'status': 'finished_failed',
            'test_mode': 'SPRT',
            'dev_time_control': '15+0.15',
            'book': 'UHO_4060_v2.epd',
            'games': 18920,
            'wins': 3820,
            'draws': 11250,
            'losses': 3850,
            'WW': 950,
            'DW': 1920,
            'DD': 7410,
            'LD': 1920,
            'LL': 930,
        },
        {
            'author': 'Anish',
            'dev_branch': 'time-manager',
            'base_branch': 'master',
            'status': 'error',
            'test_mode': 'SPRT',
            'dev_time_control': '10+0.1',
            'book': 'UHO_4060_v2.epd',
            'games': 320,
            'wins': 80,
            'draws': 160,
            'losses': 80,
        },
    ]
    
    created_tests = []
    
    for config in test_configs:
        # Déterminer les flags de statut
        status_flags = {
            'approved': False,
            'awaiting': False,
            'finished': False,
            'passed': False,
            'failed': False,
            'deleted': False,
            'error': False,
        }
        
        status = config['status']
        if status == 'pending':
            status_flags['approved'] = False
            status_flags['awaiting'] = False
        elif status == 'awaiting':
            status_flags['approved'] = False
            status_flags['awaiting'] = True
        elif status == 'active':
            status_flags['approved'] = True
            status_flags['awaiting'] = False
        elif status == 'finished_passed':
            status_flags['approved'] = True
            status_flags['finished'] = True
            status_flags['passed'] = True
        elif status == 'finished_failed':
            status_flags['approved'] = True
            status_flags['finished'] = True
            status_flags['failed'] = True
        elif status == 'error':
            status_flags['error'] = True
        
        # Créer le test
        test = Test.objects.create(
            author=config['author'],
            upload_pgns='FALSE',
            
            # Book settings
            book_name=config['book'],
            book_index=1,
            
            # Dev Engine
            dev=dev_engine,
            dev_repo='https://github.com/official-stockfish/Stockfish',
            dev_engine='Stockfish',
            dev_options='Threads=1 Hash=16',
            dev_network='',
            dev_netname='',
            dev_time_control=config['dev_time_control'],
            
            # Base Engine
            base=base_engine,
            base_repo='https://github.com/official-stockfish/Stockfish',
            base_engine='Stockfish',
            base_options='Threads=1 Hash=16',
            base_network='',
            base_netname='',
            base_time_control=config['dev_time_control'],
            
            # Test parameters
            workload_size=32,
            priority=0,
            throughput=100,
            
            # Scaling
            scale_method='BASE',
            scale_nps=0,
            
            # Adjudication
            syzygy_wdl='OPTIONAL',
            syzygy_adj='OPTIONAL',
            win_adj='movecount=3 score=400',
            draw_adj='movenumber=40 movecount=8 score=10',
            
            # Test mode
            test_mode=config['test_mode'],
            elolower=0.0 if config['test_mode'] == 'SPRT' else 0.0,
            eloupper=5.0 if config['test_mode'] == 'SPRT' else 0.0,
            alpha=0.05 if config['test_mode'] == 'SPRT' else 0.0,
            beta=0.05 if config['test_mode'] == 'SPRT' else 0.0,
            lowerllr=-2.94 if config['test_mode'] == 'SPRT' else 0.0,
            currentllr=0.0,
            upperllr=2.94 if config['test_mode'] == 'SPRT' else 0.0,
            max_games=config.get('max_games', 0),
            
            # Results
            games=config['games'],
            losses=config['losses'],
            draws=config['draws'],
            wins=config['wins'],
            LL=config.get('LL', 0),
            LD=config.get('LD', 0),
            DD=config.get('DD', 0),
            DW=config.get('DW', 0),
            WW=config.get('WW', 0),
            
            # Distribution flags
            use_tri=False,
            use_penta=True,
            
            # Status flags
            **status_flags
        )
        
        created_tests.append(test)
        print(f'✅ Test créé: {config["author"]} - {config["dev_branch"]} vs {config["base_branch"]} ({status})')
    
    print(f'\n🎉 {len(created_tests)} tests de démonstration créés avec succès!')
    print(f'📊 Accédez à http://localhost:8000/ pour voir le nouveau design en action!')
    
    return created_tests

def delete_demo_tests():
    """Supprime tous les tests de démonstration"""
    demo_tests = Test.objects.filter(author__in=['Magnus', 'Hikaru', 'Fabiano', 'Wesley', 'Alireza', 'Levon', 'Anish'])
    count = demo_tests.count()
    demo_tests.delete()
    print(f'🗑️  {count} tests de démonstration supprimés')
    
    # Nettoyer les engines inutilisés
    Engine.objects.filter(sha__in=['abc123', 'def456']).delete()
    User.objects.filter(username='demo_user').delete()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'delete':
        delete_demo_tests()
    else:
        create_demo_tests()
