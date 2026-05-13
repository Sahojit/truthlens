import { motion } from 'framer-motion'
import { Info, BookOpen, Code2, Brain, Database, Cpu } from 'lucide-react'

const ARCHITECTURE = [
  {
    layer: 'Input Layer',
    items: ['Headline text', 'Article body', 'Source URL', 'Uploaded files', 'Voice input (Web Speech API)'],
    color: 'border-accent/40 bg-accent/5',
    icon: '📥',
  },
  {
    layer: 'Preprocessing',
    items: ['Text cleaning', 'Tokenisation', 'Lemmatisation', 'Stopword removal', 'spaCy NER'],
    color: 'border-primary/40 bg-primary/5',
    icon: '⚙️',
  },
  {
    layer: 'Feature Extraction',
    items: ['TF-IDF', 'BERT embeddings', 'Sentence-BERT', 'Linguistic features (25+)', 'Emotion lexicon'],
    color: 'border-warning/40 bg-warning/5',
    icon: '🔬',
  },
  {
    layer: 'Detection Models',
    items: ['Logistic Regression', 'XGBoost', 'BiLSTM', 'BERT Classifier', 'NLI Contradiction'],
    color: 'border-purple-500/40 bg-purple-500/5',
    icon: '🤖',
  },
  {
    layer: 'Ensemble Voting',
    items: ['Weighted average: LR 20%, XGB 20%, BiLSTM 25%, BERT 35%'],
    color: 'border-success/40 bg-success/5',
    icon: '🏆',
  },
  {
    layer: 'Explainability',
    items: ['SHAP values', 'LIME explanations', 'Token highlighting', 'Feature importance chart'],
    color: 'border-pink-500/40 bg-pink-500/5',
    icon: '🔍',
  },
]

const VIVA_QA = [
  { q: 'Why use an ensemble approach?', a: 'Ensemble learning reduces variance and bias by combining complementary model strengths — traditional ML captures surface patterns while deep learning captures semantic meaning.' },
  { q: 'How does BERT help over TF-IDF?', a: 'BERT uses contextual embeddings capturing word meaning in context (e.g., "bank" in financial vs. river context), unlike TF-IDF which is frequency-based and context-free.' },
  { q: 'What is SHAP and why use it?', a: 'SHAP (SHapley Additive exPlanations) quantifies each feature\'s marginal contribution using game theory, making black-box ML models interpretable.' },
  { q: 'How is the contradiction score computed?', a: 'We use a cross-encoder NLI (Natural Language Inference) model to score whether the article body CONTRADICTS or ENTAILS the headline, with deberta-v3 as the base model.' },
  { q: 'How is AI-generated text detected?', a: 'Via burstiness analysis (AI text is unnaturally uniform in sentence length), type-token ratio, bigram entropy, and repetition patterns — without needing a separate detector model.' },
  { q: 'What datasets were used?', a: 'ISOT Fake News Dataset (44K articles), LIAR dataset (12K statements), and Kaggle Fake News dataset, balanced with SMOTE for class equality.' },
]

export default function About() {
  return (
    <div className="space-y-8 animate-fade-in max-w-4xl">
      <div className="flex items-center gap-2">
        <Info className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-2xl font-display font-bold">About TruthLens</h1>
          <p className="text-slate-400 text-sm">Architecture, methodology, and viva preparation</p>
        </div>
      </div>

      {/* Project Overview */}
      <div className="glass-card p-6">
        <div className="section-title mb-3 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary" />
          Project Overview
        </div>
        <p className="text-slate-300 leading-relaxed text-sm">
          <strong className="text-white">TruthLens</strong> is a production-grade, research-level
          misinformation detection platform that goes beyond simple keyword matching.
          It combines <strong className="text-accent">semantic understanding</strong> (BERT/Sentence-BERT),
          <strong className="text-warning"> linguistic feature engineering</strong> (25+ features),
          <strong className="text-success"> emotion manipulation detection</strong>,
          <strong className="text-primary"> source credibility scoring</strong>,
          <strong className="text-danger"> contradiction analysis</strong> (NLI),
          and <strong className="text-purple-400"> AI-generated text detection</strong> into a
          unified multi-model ensemble with full explainability via SHAP and LIME.
        </p>
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 mt-5 text-center">
          {['Semantic AI','Explainable','Multi-Model','Graph Analysis','Emotion AI','Source DB'].map(f => (
            <div key={f} className="text-xs text-slate-400 bg-white/5 rounded-xl py-2 px-1 border border-white/5">
              {f}
            </div>
          ))}
        </div>
      </div>

      {/* Architecture Pipeline */}
      <div>
        <div className="section-title flex items-center gap-2 mb-4">
          <Cpu className="w-5 h-5 text-primary" />
          Architecture Pipeline
        </div>
        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-white/10" />
          <div className="space-y-4">
            {ARCHITECTURE.map((step, i) => (
              <motion.div
                key={step.layer}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className={`flex gap-4 glass-card p-4 border ${step.color}`}
              >
                <div className="w-8 h-8 rounded-full bg-dark-800 flex items-center justify-center
                                text-base shrink-0 border border-white/10 relative z-10">
                  {step.icon}
                </div>
                <div>
                  <div className="font-semibold text-white text-sm mb-1">{step.layer}</div>
                  <div className="flex flex-wrap gap-1.5">
                    {step.items.map(item => (
                      <span key={item} className="text-xs text-slate-400 bg-white/5 px-2 py-0.5 rounded-full border border-white/5">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="glass-card p-6">
        <div className="section-title flex items-center gap-2 mb-4">
          <Code2 className="w-5 h-5 text-primary" />
          Tech Stack
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
          {[
            ['Frontend',   'React 18 · Tailwind CSS · Framer Motion · Recharts · D3.js'],
            ['Backend',    'Python FastAPI · Motor/MongoDB Atlas · JWT Auth'],
            ['NLP/ML',     'HuggingFace Transformers · Sentence-BERT · spaCy · NLTK · scikit-learn'],
            ['Deep Learning','PyTorch · TensorFlow/Keras · BiLSTM · BERT fine-tuning'],
            ['Explainability','SHAP · LIME · Attention maps · Coefficient analysis'],
            ['Deployment', 'Docker · docker-compose · Vercel (frontend) · Render (backend)'],
          ].map(([category, stack]) => (
            <div key={category} className="bg-white/5 rounded-xl p-3 border border-white/5">
              <div className="text-xs text-primary font-semibold mb-1 uppercase tracking-wider">{category}</div>
              <div className="text-xs text-slate-400 leading-relaxed">{stack}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Viva Q&A */}
      <div>
        <div className="section-title flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-primary" />
          Viva / Interview Q&A
        </div>
        <div className="space-y-3">
          {VIVA_QA.map(({ q, a }, i) => (
            <details key={i} className="glass-card group">
              <summary className="cursor-pointer list-none p-4 flex items-start gap-3 select-none">
                <span className="text-primary font-bold text-sm shrink-0">Q{i + 1}.</span>
                <span className="text-white text-sm font-medium">{q}</span>
                <span className="ml-auto text-slate-500 group-open:rotate-180 transition-transform">▾</span>
              </summary>
              <div className="px-4 pb-4 pt-0 text-slate-300 text-sm leading-relaxed border-t border-white/5">
                {a}
              </div>
            </details>
          ))}
        </div>
      </div>

      {/* Future Scope */}
      <div className="glass-card p-6">
        <div className="section-title mb-3">Future Scope</div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {[
            'Multilingual detection (Hindi, Spanish…)',
            'Real-time news stream monitoring',
            'Browser extension integration',
            'Twitter/X misinformation tracking',
            'Federated learning for privacy',
            'Claim verification with knowledge graph',
            'Sarcasm & satire detection',
            'Multi-modal (image + text) detection',
            'API public access & rate-limited SDK',
          ].map(item => (
            <div key={item} className="text-xs text-slate-400 bg-white/5 rounded-lg p-2.5 border border-white/5 flex items-start gap-2">
              <span className="text-primary mt-0.5">→</span>
              {item}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
