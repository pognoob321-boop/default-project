#!/usr/bin/env node
/**
 * Learning Method Assessment Tool
 * Tests different learning styles and finds what works best for YOU
 * Uses promise-based loops to iterate through learning methods
 */

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Prompts user for input (returns a promise)
function ask(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => resolve(answer.trim()));
  });
}

// Pauses for dramatic effect or to let user think
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ─── Learning Methods Database ────────────────────────────────────────────────
const LEARNING_METHODS = [
  {
    id: 'visual',
    name: 'Visual Learning',
    emoji: '👁️',
    description: 'Learning through images, diagrams, charts, color coding, mind maps',
    testQuestions: [
      'When you see a diagram, do you remember it better than reading the same info?',
      'Do you prefer charts/graphs over text explanations?',
      'Can you visualize concepts in your mind easily?',
      'Do you use highlighting, colors, or doodles when studying?',
      'When someone explains something, do you imagine pictures?'
    ],
    techniques: [
      'Mind mapping',
      'Color-coded notes',
      'Infographics',
      'Video tutorials with visuals',
      'Flowcharts and diagrams',
      'Anki cards with images'
    ]
  },
  {
    id: 'auditory',
    name: 'Auditory Learning',
    emoji: '👂',
    description: 'Learning through listening, discussions, lectures, podcasts, talking it out',
    testQuestions: [
      'Do you remember things you hear better than things you read?',
      'Do you talk to yourself when working through problems?',
      'Do you prefer lectures/podcasts over textbooks?',
      'Can you repeat information after hearing it once?',
      'Do you remember song lyrics easily?'
    ],
    techniques: [
      'Record yourself explaining concepts',
      'Listen to lectures/podcasts',
      'Study groups with discussion',
      'Teach concepts out loud',
      'Use text-to-speech for notes',
      'Rhythmic repetition (mnemonics)'
    ]
  },
  {
    id: 'reading',
    name: 'Read/Write Learning',
    emoji: '📖',
    description: 'Learning through reading texts, writing notes, lists, definitions',
    testQuestions: [
      'Do you prefer reading books over watching videos?',
      'Do you take detailed written notes?',
      'Do you remember things you write down?',
      'Do you like making lists, definitions, and bullet points?',
      'When learning something new, do you look it up and read about it?'
    ],
    techniques: [
      'Rewrite notes in your own words',
      'Summarize chapters in writing',
      'Create glossaries and definitions',
      'Write practice questions and answers',
      'Read multiple sources on the same topic',
      'Use Cornell note-taking method'
    ]
  },
  {
    id: 'kinesthetic',
    name: 'Kinesthetic/Doing Learning',
    emoji: '🖐️',
    description: 'Learning through hands-on practice, experiments, building, physical activity',
    testQuestions: [
      'Do you learn better by doing rather than watching/listening?',
      'Do you fidget or move around when studying?',
      'Do you prefer lab work, workshops, or projects?',
      'Can you learn a new skill just by trying it?',
      'Do you use your hands when explaining things?'
    ],
    techniques: [
      'Build projects from scratch',
      'Practice with real examples',
      'Use physical objects to model concepts',
      'Take breaks to move between study sessions',
      'Role-play scenarios',
      'Create physical flashcards you can touch'
    ]
  },
  {
    id: 'social',
    name: 'Social/Group Learning',
    emoji: '👥',
    description: 'Learning through collaboration, teaching others, group discussions',
    testQuestions: [
      'Do you learn better in groups than alone?',
      'Do you understand concepts better when you teach them?',
      'Do you enjoy debates and discussions about topics?',
      'Do you study better with a partner?',
      'When stuck, do you ask someone rather than figure it out alone?'
    ],
    techniques: [
      'Form study groups',
      'Teach concepts to others (Feynman method)',
      'Join online communities/Discord servers',
      'Debate topics with others',
      'Peer review and feedback',
      'Collaborative projects'
    ]
  },
  {
    id: 'solitary',
    name: 'Solitary/Self-Study Learning',
    emoji: '🧘',
    description: 'Learning through independent study, self-paced exploration, introspection',
    testQuestions: [
      'Do you prefer studying alone?',
      'Do you set your own learning pace?',
      'Do you enjoy deep-dive research on your own?',
      'Do you get distracted easily in groups?',
      'Do you learn better in quiet environments?'
    ],
    techniques: [
      'Structured self-study schedules',
      'Personal knowledge management (Obsidian, Notion)',
      'Deep work sessions with no distractions',
      'Self-paced online courses',
      'Journaling what you learn',
      'Spaced repetition systems (Anki)'
    ]
  }
];

// ─── Scoring Engine ──────────────────────────────────────────────────────────
class LearningAssessment {
  constructor() {
    this.scores = {};
    this.testResults = {};
    this.userCapabilities = {};
    
    // Initialize scores
    LEARNING_METHODS.forEach(method => {
      this.scores[method.id] = 0;
      this.testResults[method.id] = { correct: 0, total: 0, time: 0 };
    });
  }

  // Ask a yes/no question and return score
  async askBinary(question) {
    const answer = await ask(`${question} (yes/no/maybe): `);
    const normalized = answer.toLowerCase();
    if (normalized === 'yes' || normalized === 'y') return 2;
    if (normalized === 'maybe' || normalized === 'm') return 1;
    return 0;
  }

  // Ask rating question (1-5)
  async askRating(question) {
    const answer = await ask(`${question} (1-5, where 5 = strongly agree): `);
    const rating = parseInt(answer);
    return (rating >= 1 && rating <= 5) ? rating : 3;
  }

  // Run the initial preference questionnaire
  async runPreferenceTest() {
    console.log('\n' + '═'.repeat(60));
    console.log('  📋 PHASE 1: PREFERENCE QUESTIONNAIRE');
    console.log('═'.repeat(60));
    console.log('Answer honestly based on your experience, not what you think');
    console.log('you "should" prefer.\n');

    for (const method of LEARNING_METHODS) {
      console.log(`\n${method.emoji} ${method.name.toUpperCase()}`);
      console.log(`   ${method.description}\n`);
      
      let methodScore = 0;
      for (const question of method.testQuestions) {
        const score = await this.askBinary(`  → ${question}`);
        methodScore += score;
      }
      
      this.scores[method.id] += methodScore;
      console.log(`   Score: ${methodScore}/${method.testQuestions.length * 2}`);
      
      await delay(300); // Brief pause between sections
    }
  }

  // Run a practical learning test - teaches a concept using each method
  async runPracticalTest() {
    console.log('\n' + '═'.repeat(60));
    console.log('  🧪 PHASE 2: PRACTICAL LEARNING TEST');
    console.log('═'.repeat(60));
    console.log('I will teach you the same concept using different methods.');
    console.log('Then I will test how well you remember it.\n');

    const concept = {
      name: 'The Pareto Principle (80/20 Rule)',
      content: {
        visual: [
          '\n   📊 VISUAL REPRESENTATION:\n',
          '   ┌─────────────────────────────────────┐',
          '   │ ████░░░░░░░░░░░░░░░░ │ 20% Effort  │',
          '   │ ████████████████████ │ → 80% Results│',
          '   ├─────────────────────────────────────┤',
          '   │ ████████████████████ │ 80% Effort  │',
          '   │ ████░░░░░░░░░░░░░░░░ │ → 20% Results│',
          '   └─────────────────────────────────────┘\n',
          '   Key: Small input → Big output (Pareto optimal)\n'
        ],
        auditory: [
          '\n   🎧 AUDITORY EXPLANATION:\n',
          '   Imagine you have a class of 100 students.',
          '   The teacher realizes that just 20 of them ask',
          '   80% of the questions. That is the Pareto Principle.',
          '',
          '   In your code, 80% of bugs come from 20% of modules.',
          '   80% of revenue comes from 20% of customers.',
          '   Focus your energy on that critical 20%.\n'
        ],
        reading: [
          '\n   📖 WRITTEN EXPLANATION:\n',
          '   The Pareto Principle states that roughly 80% of effects',
          '   come from 20% of causes. Named after Vilfredo Pareto,',
          '   an Italian economist who observed in 1906 that 80% of',
          '   land in Italy was owned by 20% of the population.',
          '',
          '   Applications: prioritization, resource allocation,',
          '   time management, quality control, software debugging.\n'
        ],
        kinesthetic: [
          '\n   🖐️ HANDS-ON EXERCISE:\n',
          '   Pick up a pen and write down your last 10 tasks.',
          '   Now circle the 2 that would give you 80% value.',
          '   Cross out the bottom 5 that give minimal results.',
          '',
          '   You just applied the Pareto Principle!',
          '   The 2 circled tasks are your "vital few".\n'
        ]
      }
    };

    console.log(`📚 Today's concept: ${concept.name}\n`);
    await delay(500);

    // Teach using each method and track time
    const methodsToTest = ['visual', 'auditory', 'reading', 'kinesthetic'];
    
    for (const methodId of methodsToTest) {
      const startTime = Date.now();
      
      console.log(`\n${'─'.repeat(50)}`);
      console.log(`Teaching via: ${LEARNING_METHODS.find(m => m.id === methodId).name}`);
      console.log(`${'─'.repeat(50)}`);
      
      const content = concept.content[methodId];
      for (const line of content) {
        console.log(line);
        await delay(200); // Simulate reading time
      }
      
      const endTime = Date.now();
      this.testResults[methodId].time = (endTime - startTime) / 1000;
      
      await ask('\n  [Press Enter when you\'re ready to continue]');
    }

    // Now test recall
    console.log('\n' + '═'.repeat(60));
    console.log('  📝 RECALL TEST');
    console.log('═'.repeat(60));
    console.log('Answer these questions about what you just learned:\n');

    const testQuestions = [
      {
        q: 'What is the Pareto Principle also called?',
        a: ['80/20', '80 20', 'eighty twenty', '80/20 rule']
      },
      {
        q: 'Who was the Italian economist who observed this principle?',
        a: ['pareto', 'vilfredo pareto']
      },
      {
        q: 'In what year did Pareto make his observation?',
        a: ['1906']
      },
      {
        q: 'According to the principle, what percentage of effects come from what percentage of causes?',
        a: ['80% from 20%', '80 20', '80 from 20']
      }
    ];

    for (const test of testQuestions) {
      const answer = await ask(`  Q: ${test.q}\n  Your answer: `);
      const isCorrect = test.a.some(a => 
        answer.toLowerCase().includes(a.toLowerCase())
      );
      
      if (isCorrect) {
        console.log('  ✅ Correct!\n');
        // Award points to all methods (concept was learned)
        methodsToTest.forEach(m => this.testResults[m].correct++);
      } else {
        console.log(`  ❌ Incorrect. The answer was: ${test.a[0]}\n`);
      }
      methodsToTest.forEach(m => this.testResults[m].total++);
    }
  }

  // Identify user capabilities and preferences
  async assessCapabilities() {
    console.log('\n' + '═'.repeat(60));
    console.log('  🎯 PHASE 3: CAPABILITY ASSESSMENT');
    console.log('═'.repeat(60));
    console.log('Let us understand your learning environment and habits.\n');

    const capabilities = [
      { key: 'dailyHours', q: 'How many hours per day can you dedicate to learning? ', type: 'number' },
      { key: 'attentionSpan', q: 'How long can you focus before getting distracted (in minutes)? ', type: 'number' },
      { key: 'hasQuietSpace', q: 'Do you have a quiet study space? (yes/no): ', type: 'boolean' },
      { key: 'socialPreference', q: 'Do you prefer studying alone or with others? (alone/social/both): ', type: 'string' },
      { tech: 'techComfort', q: 'How comfortable are you with technology for learning (1-5)? ', type: 'number' },
      { key: 'budget', q: 'Monthly budget for learning resources in USD (0 = free only): ', type: 'number' },
      { key: 'goal', q: 'What is your primary learning goal? (e.g., coding, language, math, general): ', type: 'string' }
    ];

    for (const cap of capabilities) {
      const answer = await ask(`  ${cap.q}`);
      if (cap.type === 'number') {
        this.userCapabilities[cap.key] = parseInt(answer) || 0;
      } else {
        this.userCapabilities[cap.key] = answer;
      }
    }

    console.log('\n  📊 Your Learning Profile:');
    console.log(`     Daily study time: ${this.userCapabilities.dailyHours} hours`);
    console.log(`     Attention span: ${this.userCapabilities.attentionSpan} minutes`);
    console.log(`     Study space: ${this.userCapabilities.hasQuietSpace}`);
    console.log(`     Social preference: ${this.userCapabilities.socialPreference}`);
    console.log(`     Tech comfort: ${this.userCapabilities.techComfort}/5`);
    console.log(`     Budget: $${this.userCapabilities.budget}/month`);
    console.log(`     Goal: ${this.userCapabilities.goal}`);
  }

  // Calculate final scores and generate recommendations
  calculateResults() {
    // Normalize scores from preference test (0-10 scale)
    LEARNING_METHODS.forEach(method => {
      const maxPossible = method.testQuestions.length * 2;
      const normalized = (this.scores[method.id] / maxPossible) * 10;
      this.scores[method.id] = normalized;
    });

    // Add bonus from practical test (if available)
    for (const [methodId, result] of Object.entries(this.testResults)) {
      if (result.total > 0) {
        const accuracy = result.correct / result.total;
        this.scores[methodId] += accuracy * 5; // Up to 5 bonus points
      }
    }

    // Apply capability modifiers
    const { dailyHours, attentionSpan, hasQuietSpace, socialPreference, techComfort } = this.userCapabilities;
    
    // Solitary learners get bonus if they have quiet space
    if (hasQuietSpace === 'yes') this.scores.solitary += 1.5;
    
    // Social learners get bonus if they prefer groups
    if (socialPreference === 'social' || socialPreference === 'both') this.scores.social += 2;
    
    // Tech-savvy learners benefit more from visual/digital methods
    if (techComfort >= 4) {
      this.scores.visual += 1;
      this.scores.reading += 0.5;
    }
    
    // Short attention spans favor kinesthetic learning
    if (attentionSpan < 20) {
      this.scores.kinesthetic += 2;
      this.scores.auditory += 1;
    }

    // Sort methods by score
    const ranked = LEARNING_METHODS
      .map(m => ({ ...m, score: this.scores[m.id] }))
      .sort((a, b) => b.score - a.score);

    return ranked;
  }

  // Generate personalized learning plan
  generatePlan(ranked) {
    const top3 = ranked.slice(0, 3);
    const { dailyHours, goal, budget } = this.userCapabilities;

    console.log('\n' + '═'.repeat(60));
    console.log('  🎓 YOUR PERSONALIZED LEARNING PROFILE');
    console.log('═'.repeat(60));

    console.log('\n  📊 LEARNING METHOD RANKINGS:\n');
    ranked.forEach((method, i) => {
      const bar = '█'.repeat(Math.round(method.score)) + '░'.repeat(10 - Math.round(method.score));
      const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '  ';
      console.log(`  ${medal} ${method.emoji} ${method.name.padEnd(25)} [${bar}] ${method.score.toFixed(1)}/15`);
    });

    console.log('\n' + '─'.repeat(60));
    console.log('  🏆 TOP 3 LEARNING METHODS FOR YOU:\n');
    
    top3.forEach((method, i) => {
      console.log(`  ${i + 1}. ${method.emoji} ${method.name}`);
      console.log(`     Best techniques:`);
      method.techniques.slice(0, 3).forEach(t => console.log(`       • ${t}`));
      console.log('');
    });

    // Generate time allocation
    console.log('─'.repeat(60));
    console.log('  ⏰ RECOMMENDED TIME ALLOCATION:\n');
    
    const totalScore = top3.reduce((sum, m) => sum + m.score, 0);
    const dailyMinutes = dailyHours * 60;
    
    top3.forEach((method, i) => {
      const percentage = Math.round((method.score / totalScore) * 100);
      const minutes = Math.round((method.score / totalScore) * dailyMinutes);
      console.log(`  ${method.emoji} ${method.name.padEnd(25)} ${percentage}% → ${minutes} min/day`);
    });

    // Generate study schedule
    console.log('\n' + '─'.repeat(60));
    console.log('  📅 SUGGESTED DAILY SCHEDULE:\n');
    
    let timeLeft = dailyMinutes;
    const schedule = [];
    
    top3.forEach((method, i) => {
      const minutes = Math.round((method.score / totalScore) * dailyMinutes);
      const pomodoros = Math.ceil(minutes / 25);
      schedule.push({
        method: method.name,
        emoji: method.emoji,
        minutes,
        pomodoros,
        techniques: method.techniques.slice(0, 2)
      });
      timeLeft -= minutes;
    });

    schedule.forEach((block, i) => {
      console.log(`  Block ${i + 1}: ${block.emoji} ${block.method}`);
      console.log(`           Duration: ${block.minutes} minutes (${block.pomodoros} pomodoros)`);
      console.log(`           Try: ${block.techniques.join(' and ')}`);
      console.log('');
    });

    // Save results to JSON
    const results = {
      timestamp: new Date().toISOString(),
      rankings: ranked.map(m => ({ name: m.name, score: m.score.toFixed(2) })),
      topMethods: top3.map(m => m.name),
      capabilities: this.userCapabilities,
      schedule,
      techniques: top3.flatMap(m => m.techniques)
    };

    return results;
  }

  // Run the complete assessment
  async run() {
    console.log('\n' + '╔' + '═'.repeat(58) + '╗');
    console.log('║' + '  🧠 LEARNING METHOD ASSESSMENT TOOL'.padEnd(58) + '║');
    console.log('║' + '  Find out how YOU learn best'.padEnd(58) + '║');
    console.log('╚' + '═'.repeat(58) + '╝');
    console.log('\n  This tool will:');
    console.log('  1. Ask about your learning preferences');
    console.log('  2. Teach you something using different methods');
    console.log('  3. Test what you remember');
    console.log('  4. Analyze your capabilities');
    console.log('  5. Generate a personalized learning plan\n');

    const start = await ask('  Ready to begin? (yes/no): ');
    if (start.toLowerCase() !== 'yes' && start.toLowerCase() !== 'y') {
      console.log('\n  No worries! Come back when you are ready.\n');
      rl.close();
      return;
    }

    // Phase 1: Preference questionnaire
    await this.runPreferenceTest();

    // Phase 2: Practical learning test
    await this.runPracticalTest();

    // Phase 3: Capability assessment
    await this.assessCapabilities();

    // Calculate and display results
    const ranked = this.calculateResults();
    const results = this.generatePlan(ranked);

    // Save results
    const fs = require('fs');
    const outputPath = './learning-results.json';
    fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
    console.log(`\n  💾 Results saved to: ${outputPath}`);

    // Final summary
    console.log('\n' + '═'.repeat(60));
    console.log('  🎯 KEY TAKEAWAYS\n');
    console.log(`  Your dominant learning style: ${results.rankings[0].name}`);
    console.log(`  You learn best with: ${results.topMethods.slice(0, 2).join(' and ')}`);
    console.log(`  Recommended study time: ${this.userCapabilities.dailyHours} hours/day`);
    console.log(`  Focus on: ${results.techniques.slice(0, 3).join(', ')}`);
    console.log('\n  💡 Remember: Everyone learns differently, and your optimal');
    console.log('     mix may change over time. Retake this assessment periodically!\n');

    rl.close();
    return results;
  }
}

// ─── Promise-Based Loop Demo ──────────────────────────────────────────────────
// Shows how promises work in loops
async function demonstratePromiseLoop() {
  console.log('\n' + '─'.repeat(60));
  console.log('  🔄 BONUS: Promise-Based Loop Concepts\n');
  
  // Sequential loop with promises
  console.log('  📌 Sequential Promise Loop:');
  const methods = ['visual', 'auditory', 'reading', 'kinesthetic'];
  
  for (const method of methods) {
    // Simulate async operation
    await new Promise(resolve => {
      setTimeout(() => {
        console.log(`     Processing: ${method}`);
        resolve();
      }, 100);
    });
  }

  // Parallel loop with promises
  console.log('\n  📌 Parallel Promise Loop:');
  const promises = methods.map(method => 
    new Promise(resolve => {
      setTimeout(() => {
        resolve(`     Completed: ${method}`);
      }, 100);
    })
  );
  
  const results = await Promise.all(promises);
  results.forEach(r => console.log(r));

  // Promise.allSettled for error handling
  console.log('\n  📌 Promise.allSettled (handles failures):');
  const mixedPromises = methods.map((method, i) =>
    new Promise((resolve, reject) => {
      setTimeout(() => {
        if (i === 2) reject(`${method} failed`); // Simulate one failure
        else resolve(`${method} succeeded`);
      }, 100);
    })
  );

  const settled = await Promise.allSettled(mixedPromises);
  settled.forEach(result => {
    if (result.status === 'fulfilled') {
      console.log(`     ✅ ${result.value}`);
    } else {
      console.log(`     ❌ ${result.reason}`);
    }
  });
}

// ─── Main Entry Point ────────────────────────────────────────────────────────
async function main() {
  const assessment = new LearningAssessment();
  
  // Run the full assessment
  const results = await assessment.run();
  
  // Demonstrate promise loops
  await demonstratePromiseLoop();
  
  console.log('\n  ✨ Good luck with your learning journey!\n');
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { LearningAssessment, LEARNING_METHODS };
