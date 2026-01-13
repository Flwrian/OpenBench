// Système de mise à jour en temps réel pour OpenBench
// Mise à jour automatique des statistiques des tests sans recharger la page

(function() {
    'use strict';
    
    const POLL_INTERVAL = 3000; // Mise à jour toutes les 3 secondes
    let pollTimer = null;
    let testElements = new Map(); // Map: test_id -> { element, lastData }
    
    // Initialise le système de polling
    function init() {
        // Cherche tous les tests actifs sur la page
        findActiveTests();
        
        if (testElements.size > 0) {
            console.log(`[Live Updates] Monitoring ${testElements.size} active test(s)`);
            startPolling();
        }
    }
    
    // Trouve tous les éléments de test sur la page
    function findActiveTests() {
        // Cherche les lignes de test dans le tableau
        const testRows = document.querySelectorAll('tr[data-test-id]');
        
        testRows.forEach(row => {
            const testId = parseInt(row.dataset.testId);
            const statblock = row.querySelector('.statblock');
            const wdlBar = row.querySelector('.wdl-bar-container');
            
            if (statblock && wdlBar) {
                testElements.set(testId, {
                    row: row,
                    statblock: statblock,
                    wdlBar: wdlBar,
                    lastData: null
                });
            }
        });
    }
    
    // Démarre le polling
    function startPolling() {
        if (pollTimer) return;
        
        // Première mise à jour immédiate
        pollStats();
        
        // Puis toutes les POLL_INTERVAL ms
        pollTimer = setInterval(pollStats, POLL_INTERVAL);
    }
    
    // Arrête le polling
    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
            console.log('[Live Updates] Polling stopped');
        }
    }
    
    // Récupère les stats depuis l'API
    async function pollStats() {
        const testIds = Array.from(testElements.keys());
        
        if (testIds.length === 0) {
            stopPolling();
            return;
        }
        
        try {
            const response = await fetch(`/api/live-stats/?ids=${testIds.join(',')}`);
            
            if (!response.ok) {
                console.error('[Live Updates] API error:', response.status);
                return;
            }
            
            const data = await response.json();
            
            if (data.stats) {
                updateTestElements(data.stats);
            }
        } catch (error) {
            console.error('[Live Updates] Fetch error:', error);
        }
    }
    
    // Met à jour les éléments du DOM avec les nouvelles stats
    function updateTestElements(stats) {
        for (const [testId, newData] of Object.entries(stats)) {
            const element = testElements.get(parseInt(testId));
            
            if (!element) continue;
            
            const oldData = element.lastData;
            
            // Si les données ont changé, met à jour
            if (!oldData || hasChanged(oldData, newData)) {
                updateWDLBar(element.wdlBar, newData);
                updateStatBlock(element.statblock, newData);
                
                // Ajoute une animation flash si les données ont changé
                if (oldData && (oldData.games !== newData.games)) {
                    flashUpdate(element.row);
                }
                
                element.lastData = newData;
            }
            
            // Si le test est terminé, arrête de le surveiller
            if (newData.finished) {
                testElements.delete(parseInt(testId));
                
                // Recharge la page si tous les tests sont finis (pour voir le résultat final)
                if (testElements.size === 0) {
                    console.log('[Live Updates] All tests finished, reloading page...');
                    setTimeout(() => location.reload(), 2000);
                }
            }
        }
    }
    
    // Vérifie si les données ont changé
    function hasChanged(oldData, newData) {
        return oldData.games !== newData.games ||
               oldData.wins !== newData.wins ||
               oldData.draws !== newData.draws ||
               oldData.losses !== newData.losses;
    }
    
    // Met à jour la barre WDL
    function updateWDLBar(container, data) {
        if (data.games === 0) return;
        
        const winPct = (data.wins / data.games) * 100;
        const drawPct = (data.draws / data.games) * 100;
        const lossPct = (data.losses / data.games) * 100;
        
        const segments = container.querySelectorAll('.wdl-segment');
        
        if (segments.length === 3) {
            // Ordre: win, draw, loss
            segments[0].style.width = winPct + '%';
            segments[0].title = `Wins: ${data.wins} (${winPct.toFixed(1)}%)`;
            
            segments[1].style.width = drawPct + '%';
            segments[1].title = `Draws: ${data.draws} (${drawPct.toFixed(1)}%)`;
            
            segments[2].style.width = lossPct + '%';
            segments[2].title = `Losses: ${data.losses} (${lossPct.toFixed(1)}%)`;
        }
    }
    
    // Met à jour le bloc de statistiques
    function updateStatBlock(statblock, data) {
        // Récupère le contenu textuel et le met à jour
        const strong = statblock.querySelector('strong');
        if (!strong) return;
        
        // Parse le contenu existant pour garder le format
        const lines = strong.innerHTML.split('<br>');
        
        // Met à jour la ligne "Games: N W: X L: Y D: Z"
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('Games:')) {
                lines[i] = `Games: ${data.games} W: ${data.wins} L: ${data.losses} D: ${data.draws}`;
            }
            if (lines[i].includes('Ptnml')) {
                lines[i] = `Ptnml(0-2): ${data.LL}, ${data.LD}, ${data.DD}, ${data.DW}, ${data.WW}`;
            }
            if (lines[i].includes('LLR:') && data.currentllr !== null) {
                // Garde le format existant mais met à jour la valeur LLR
                const parts = lines[i].split(' ');
                if (parts.length > 1) {
                    parts[1] = data.currentllr.toFixed(2);
                    lines[i] = parts.join(' ');
                }
            }
        }
        
        strong.innerHTML = lines.join('<br>');
    }
    
    // Ajoute un effet visuel flash pour indiquer une mise à jour
    function flashUpdate(row) {
        row.style.transition = 'background-color 0.3s ease';
        const originalBg = row.style.backgroundColor;
        row.style.backgroundColor = 'rgba(94, 234, 212, 0.15)';
        
        setTimeout(() => {
            row.style.backgroundColor = originalBg;
        }, 300);
    }
    
    // Arrête le polling quand l'utilisateur quitte la page
    window.addEventListener('beforeunload', stopPolling);
    
    // Arrête le polling quand l'onglet n'est plus visible
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopPolling();
        } else if (testElements.size > 0) {
            startPolling();
        }
    });
    
    // Initialise quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
