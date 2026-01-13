#!/usr/bin/env python3
"""
Script rapide pour générer des données de test OpenBench
Usage:
    python Scripts/quick_mock.py          # Génère 10 tests
    python Scripts/quick_mock.py 25       # Génère 25 tests
    python Scripts/quick_mock.py clear    # Supprime tous les tests
"""
import os
import sys
import random
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OpenSite.settings')
django.setup()

from django.contrib.auth.models import User
from OpenBench.models import Test, Engine, Profile

def quick_mock(n=10):
    """Génération rapide de tests"""
    
    # Utilisateurs
    users = []
    for name in ['magnus', 'hikaru', 'fabiano', 'wesley']:
        user, _ = User.objects.get_or_create(username=name, defaults={'email': f'{name}@test.com'})
        if not hasattr(user, 'profile'):
            Profile.objects.get_or_create(user=user)
        users.append(user)
    
    # Moteur
    engine, _ = Engine.objects.get_or_create(
        name='Stockfish',
        defaults={'source': 'https://github.com/official-stockfish/Stockfish', 'sha': '0'*40, 'bench': 5000000}
    )
    
    statuses = ['active', 'finished_passed', 'finished_failed', 'pending', 'awaiting']
    repos = [
        'https://github.com/official-stockfish/Stockfish',
        'https://github.com/AndyGrant/Ethereal',
        'https://github.com/jhonnold/berserk'
    ]
    books = ['8moves_v3.epd', 'UHO_4060_v2.epd', 'DFRC.epd', 'Pohl.epd']
    tcs = ['8+0.08', '10+0.1', '20+0.2', '40+0.4', '60+0.6']
    
    print(f"🚀 Génération de {n} tests...")
    
    for i in range(n):
        status = random.choice(statuses)
        
        # Résultats
        if status in ['awaiting', 'pending']:
            g, w, d, l = 0, 0, 0, 0
        elif status == 'active':
            g = random.randint(3000, 15000)
            d = int(g * random.uniform(0.45, 0.65))
            w = int((g - d) * random.uniform(0.48, 0.52))
            l = g - w - d
        elif status == 'finished_passed':
            g = random.randint(15000, 40000)
            d = int(g * random.uniform(0.40, 0.60))
            w = int((g - d) * random.uniform(0.52, 0.58))
            l = g - w - d
        else:  # failed
            g = random.randint(10000, 35000)
            d = int(g * random.uniform(0.40, 0.60))
            l = int((g - d) * random.uniform(0.52, 0.58))
            w = g - d - l
        
        # Pentanomial
        WW = int(w * 0.3) if w > 0 else 0
        DW = w - WW
        LL = int(l * 0.3) if l > 0 else 0
        LD = l - LL
        DD = d
        
        # Statuts booléens
        test_passed = (status == 'finished_passed')
        test_failed = (status == 'finished_failed')
        test_finished = test_passed or test_failed
        test_approved = status not in ['pending', 'awaiting']
        test_awaiting = (status == 'awaiting')
        
        test = Test.objects.create(
            author=random.choice(users).username,
            dev=engine,
            base=engine,
            dev_repo=random.choice(repos),
            base_repo=random.choice(repos),
            dev_engine=engine.name,
            base_engine=engine.name,
            dev_options='',
            base_options='',
            book_name=random.choice(books),
            dev_time_control=random.choice(tcs),
            base_time_control=random.choice(tcs),
            test_mode='SPRT',
            games=g, wins=w, draws=d, losses=l,
            WW=WW, DW=DW, DD=DD, LD=LD, LL=LL,
            passed=test_passed,
            failed=test_failed,
            finished=test_finished,
            approved=test_approved,
            awaiting=test_awaiting,
            use_penta=True,
            priority=random.randint(0, 10),
            throughput=random.randint(800, 1500),
            elolower=random.uniform(-1.5, 2.0),
            eloupper=random.uniform(2.5, 5.5),
            currentllr=random.uniform(-1.0, 2.8),
            lowerllr=-2.94,
            upperllr=2.94,
            win_adj='movecount=3 score=400',
            draw_adj='movenumber=40 movecount=8 score=10',
            upload_pgns='FALSE'
        )
        
        emoji = {'active':'🟢', 'finished_passed':'✅', 'finished_failed':'❌', 'pending':'🕐', 'awaiting':'⏳'}
        print(f"{emoji.get(status,'❓')} Test #{test.id}: {engine.name} | W:{w} D:{d} L:{l}")
    
    print(f"\n✅ {n} tests créés!")
    print(f"🌐 http://localhost:8000/")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'clear':
            c = Test.objects.count()
            Test.objects.all().delete()
            print(f"🗑️  {c} tests supprimés")
        else:
            quick_mock(int(sys.argv[1]))
    else:
        quick_mock(10)
