<!-- HR Dashboard untuk Skrining Psikologis -->
<!-- File: frontend/src/routes/hr/dashboard/+page.svelte -->

<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  
  let candidates = writable([]);
  let selectedCandidate = null;
  let filter = 'all'; // all, dokter, perawat, bidan
  let loading = true;
  let searchQuery = '';

  onMount(async () => {
    try {
      const response = await fetch('/api/psychological/dashboard/candidates');
      const data = await response.json();
      candidates.set(data.candidates || []);
      loading = false;
    } catch (error) {
      console.error('Error loading candidates:', error);
      loading = false;
    }
  });

  function getRecommendationBadge(recommendation) {
    const badges = {
      'PROCEED': { 
        color: 'bg-green-100', 
        text: 'text-green-800', 
        icon: '✅',
        label: 'Lanjut' 
      },
      'FURTHER_ASSESSMENT': { 
        color: 'bg-yellow-100', 
        text: 'text-yellow-800',
        icon: '⚠️', 
        label: 'Verifikasi' 
      },
      'CAUTION': { 
        color: 'bg-red-100', 
        text: 'text-red-800',
        icon: '❌',
        label: 'Hati-Hati' 
      }
    };
    return badges[recommendation] || badges['FURTHER_ASSESSMENT'];
  }

  function getScoreColor(score) {
    if (score >= 4.0) return 'text-green-600 font-bold';
    if (score >= 3.5) return 'text-blue-600 font-bold';
    if (score >= 3.0) return 'text-yellow-600 font-bold';
    return 'text-red-600 font-bold';
  }

  function filteredCandidates() {
    let filtered = $candidates;
    
    if (filter !== 'all') {
      filtered = filtered.filter(c => c.position?.toLowerCase() === filter.toLowerCase());
    }
    
    if (searchQuery) {
      filtered = filtered.filter(c => 
        c.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.email?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    return filtered;
  }

  async function exportReport(candidate) {
    try {
      const response = await fetch(`/api/psychological/reports/export/${candidate.id}`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `psikotes_${candidate.name}_${new Date().toISOString().split('T')[0]}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Error exporting report: ' + error.message);
    }
  }

  function getPositionIcon(position) {
    const icons = {
      'dokter': '👨‍⚕️',
      'perawat': '👩‍⚕️',
      'bidan': '👶'
    };
    return icons[position?.toLowerCase()] || '👤';
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
  <!-- Header -->
  <div class="mb-8 bg-white rounded-lg shadow-lg p-6">
    <h1 class="text-4xl font-bold text-gray-900 mb-2">🏥 Dashboard Skrining Psikologis HR</h1>
    <p class="text-gray-600 text-lg">Sistem penilaian awal calon karyawan rumah sakit</p>
  </div>

  <!-- Search & Filter Section -->
  <div class="mb-6 bg-white rounded-lg shadow-md p-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <input
        type="text"
        placeholder="Cari nama atau email kandidat..."
        bind:value={searchQuery}
        class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <div class="flex gap-2">
        <button 
          on:click={() => filter = 'all'}
          class={`px-4 py-2 rounded-lg font-semibold transition ${
            filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Semua
        </button>
        <button 
          on:click={() => filter = 'dokter'}
          class={`px-4 py-2 rounded-lg font-semibold transition ${
            filter === 'dokter' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          👨‍⚕️ Dokter
        </button>
        <button 
          on:click={() => filter = 'perawat'}
          class={`px-4 py-2 rounded-lg font-semibold transition ${
            filter === 'perawat' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          👩‍⚕️ Perawat
        </button>
        <button 
          on:click={() => filter = 'bidan'}
          class={`px-4 py-2 rounded-lg font-semibold transition ${
            filter === 'bidan' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          👶 Bidan
        </button>
      </div>
    </div>
  </div>

  {#if loading}
    <div class="text-center py-12 bg-white rounded-lg shadow-md">
      <p class="text-gray-600 text-lg">⏳ Memuat data...</p>
    </div>
  {:else if filteredCandidates().length === 0}
    <div class="text-center py-12 bg-white rounded-lg shadow-md">
      <p class="text-gray-600 text-lg">📭 Tidak ada data kandidat</p>
    </div>
  {:else}
    <!-- Candidates Table -->
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
          <tr>
            <th class="px-6 py-4 text-left text-sm font-semibold">Nama Kandidat</th>
            <th class="px-6 py-4 text-left text-sm font-semibold">Posisi</th>
            <th class="px-6 py-4 text-left text-sm font-semibold">Tanggal Tes</th>
            <th class="px-6 py-4 text-center text-sm font-semibold">Score</th>
            <th class="px-6 py-4 text-center text-sm font-semibold">Rekomendasi</th>
            <th class="px-6 py-4 text-center text-sm font-semibold">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          {#each filteredCandidates() as candidate (candidate.id)}
            <tr class="hover:bg-blue-50 transition">
              <td class="px-6 py-4 text-sm font-medium text-gray-900">{candidate.name}</td>
              <td class="px-6 py-4 text-sm text-gray-600">{getPositionIcon(candidate.position)} {candidate.position}</td>
              <td class="px-6 py-4 text-sm text-gray-600">{candidate.test_date ? new Date(candidate.test_date).toLocaleDateString('id-ID') : 'Belum tes'}</td>
              <td class="px-6 py-4 text-sm text-center">
                {#if candidate.overall_score}
                  <span class={getScoreColor(candidate.overall_score)}>
                    {candidate.overall_score.toFixed(2)}/5.0
                  </span>
                {:else}
                  <span class="text-gray-400">-</span>
                {/if}
              </td>
              <td class="px-6 py-4 text-sm text-center">
                {#if candidate.recommendation}
                  <span class={`px-3 py-1 rounded-full text-xs font-semibold inline-block ${
                    getRecommendationBadge(candidate.recommendation).color
                  } ${getRecommendationBadge(candidate.recommendation).text}`}>
                    {getRecommendationBadge(candidate.recommendation).icon} {getRecommendationBadge(candidate.recommendation).label}
                  </span>
                {:else}
                  <span class="text-gray-400 text-xs">Menunggu</span>
                {/if}
              </td>
              <td class="px-6 py-4 text-sm text-center space-x-2">
                <button 
                  on:click={() => selectedCandidate = candidate}
                  class="text-blue-600 hover:text-blue-900 font-semibold hover:underline"
                >
                  📋 Detail
                </button>
                {#if candidate.overall_score}
                  <button 
                    on:click={() => exportReport(candidate)}
                    class="text-green-600 hover:text-green-900 font-semibold hover:underline"
                  >
                    📥 Export
                  </button>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

  <!-- Candidate Detail Modal -->
  {#if selectedCandidate}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Modal Header -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 sticky top-0">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="text-2xl font-bold">{selectedCandidate.name}</h2>
              <p class="text-blue-100">{getPositionIcon(selectedCandidate.position)} {selectedCandidate.position} • {selectedCandidate.test_date ? new Date(selectedCandidate.test_date).toLocaleDateString('id-ID') : '-'}</p>
            </div>
            <button 
              on:click={() => selectedCandidate = null}
              class="text-2xl hover:bg-blue-700 p-2 rounded-lg transition"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Content -->
        <div class="p-6 space-y-6">
          <!-- Overall Score -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 p-4 rounded">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-bold text-gray-900">Hasil Tes Keseluruhan</h3>
              {#if selectedCandidate.recommendation}
                <span class={`px-4 py-2 rounded-full text-sm font-bold ${
                  getRecommendationBadge(selectedCandidate.recommendation).color
                } ${getRecommendationBadge(selectedCandidate.recommendation).text}`}>
                  {getRecommendationBadge(selectedCandidate.recommendation).icon} {getRecommendationBadge(selectedCandidate.recommendation).label}
                </span>
              {/if}
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-gray-600 text-sm">Score Keseluruhan</p>
                <p class="text-4xl font-bold text-blue-600">{selectedCandidate.overall_score?.toFixed(2) || '-'}</p>
              </div>
              <div>
                <p class="text-gray-600 text-sm">Status</p>
                <p class="text-2xl font-bold text-gray-900">
                  {selectedCandidate.recommendation === 'PROCEED' ? '✓ LANJUT' : 
                   selectedCandidate.recommendation === 'FURTHER_ASSESSMENT' ? '⚠ VERIFIKASI' : 
                   '❌ HATI-HATI'}
                </p>
              </div>
            </div>
          </div>

          <!-- Personality Scores -->
          <div>
            <h3 class="text-lg font-bold text-gray-900 mb-4">📊 Skor Kepribadian (Big Five)</h3>
            <div class="space-y-3">
              {#each Object.entries(selectedCandidate.personality_scores || {}) as [trait, score]}
                <div class="flex items-center justify-between">
                  <div class="w-40">
                    <p class="text-sm font-semibold text-gray-700">{trait}</p>
                  </div>
                  <div class="flex-1 bg-gray-200 rounded-full h-2 mx-4">
                    <div class="bg-blue-600 h-2 rounded-full transition-all" style="width: {(score / 5) * 100}%"></div>
                  </div>
                  <span class={`text-sm font-bold w-12 text-right ${getScoreColor(score)}`}>{score.toFixed(2)}</span>
                </div>
              {/each}
            </div>
          </div>

          <!-- Stress & Resilience -->
          <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
            <h3 class="text-lg font-bold text-gray-900 mb-3">⚡ Ketahanan Stress</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-600">Penanganan Stress</p>
                <p class="text-2xl font-bold text-yellow-600">{selectedCandidate.stress_resilience?.handling?.toFixed(2) || '-'}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Resiliensi Umum</p>
                <p class="text-2xl font-bold text-yellow-600">{selectedCandidate.stress_resilience?.resilience?.toFixed(2) || '-'}</p>
              </div>
            </div>
          </div>

          <!-- Emotional Intelligence -->
          <div class="bg-purple-50 border-l-4 border-purple-500 p-4 rounded">
            <h3 class="text-lg font-bold text-gray-900 mb-3">❤️ Emotional Intelligence</h3>
            <div class="grid grid-cols-2 gap-4 text-sm">
              {#each Object.entries(selectedCandidate.emotional_intelligence || {}) as [category, score]}
                <div>
                  <p class="text-gray-600">{category}</p>
                  <p class="font-bold text-purple-600">{score.toFixed(2)}</p>
                </div>
              {/each}
            </div>
          </div>

          <!-- Red Flags -->
          {#if selectedCandidate.red_flags && selectedCandidate.red_flags.length > 0}
            <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <h3 class="text-lg font-bold text-red-900 mb-3">🚩 Indikasi Perhatian</h3>
              <ul class="space-y-2">
                {#each selectedCandidate.red_flags as flag}
                  <li class="text-sm text-red-800">{flag}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <!-- HR Recommendation -->
          <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <h3 class="text-lg font-bold text-blue-900 mb-3">💡 Rekomendasi untuk HR</h3>
            <p class="text-sm text-blue-800 mb-3">{selectedCandidate.hr_recommendation || '-'}</p>
            <p class="text-xs text-blue-700 font-semibold">📍 Langkah Selanjutnya: {selectedCandidate.next_step || '-'}</p>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3 pt-4 border-t">
            {#if selectedCandidate.overall_score}
              <button 
                on:click={() => exportReport(selectedCandidate)}
                class="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition"
              >
                📥 Export Laporan
              </button>
            {/if}
            <button 
              on:click={() => selectedCandidate = null}
              class="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg transition"
            >
              Tutup
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style global>
  :global(body) {
    @apply bg-gray-50;
  }
</style>