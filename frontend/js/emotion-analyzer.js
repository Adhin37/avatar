/**
 * Emotion Analyzer
 * Analyzes text for emotional content and sentiment to drive avatar expressions
 */

export class EmotionAnalyzer {
    constructor() {
        this.emotionKeywords = {
            happy: {
                primary: ['happy', 'joy', 'joyful', 'glad', 'pleased', 'delighted', 'cheerful', 'elated', 'ecstatic', 'blissful'],
                secondary: ['great', 'awesome', 'wonderful', 'fantastic', 'amazing', 'excellent', 'brilliant', 'perfect', 'love', 'like'],
                tertiary: ['smile', 'laugh', 'celebrate', 'party', 'fun', 'good', 'nice', 'cool', 'sweet', 'yay']
            },
            sad: {
                primary: ['sad', 'sorrow', 'grief', 'melancholy', 'depressed', 'miserable', 'heartbroken', 'devastated', 'dejected', 'gloomy'],
                secondary: ['cry', 'tears', 'weep', 'mourn', 'hurt', 'pain', 'lonely', 'empty', 'lost', 'broken'],
                tertiary: ['sorry', 'unfortunate', 'disappointed', 'regret', 'miss', 'down', 'blue', 'low', 'dark']
            },
            angry: {
                primary: ['angry', 'rage', 'fury', 'mad', 'furious', 'livid', 'irate', 'outraged', 'incensed', 'enraged'],
                secondary: ['hate', 'despise', 'loathe', 'detest', 'annoyed', 'irritated', 'frustrated', 'upset', 'pissed', 'agitated'],
                tertiary: ['stupid', 'idiot', 'damn', 'hell', 'awful', 'terrible', 'horrible', 'disgusting', 'sick']
            },
            surprised: {
                primary: ['surprised', 'shock', 'shocked', 'astonished', 'amazed', 'stunned', 'bewildered', 'astounded', 'flabbergasted'],
                secondary: ['wow', 'omg', 'incredible', 'unbelievable', 'unexpected', 'sudden', 'whoa', 'really', 'seriously'],
                tertiary: ['what', 'how', 'why', 'no way', 'cant believe', 'never thought', 'didnt expect']
            },
            fearful: {
                primary: ['fear', 'afraid', 'scared', 'terrified', 'horrified', 'petrified', 'panic', 'anxious', 'worried', 'nervous'],
                secondary: ['danger', 'threat', 'risk', 'unsafe', 'trouble', 'problem', 'concern', 'stress', 'tension'],
                tertiary: ['help', 'please', 'careful', 'watch out', 'be careful', 'scared me', 'frightening']
            },
            disgusted: {
                primary: ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated', 'appalled', 'grossed out'],
                secondary: ['gross', 'yuck', 'ew', 'nasty', 'awful', 'terrible', 'horrible', 'vile', 'repugnant'],
                tertiary: ['cant stand', 'makes me sick', 'disgusting', 'revolting', 'nasty', 'icky']
            }
        };
        
        this.contextKeywords = {
            greeting: ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'welcome', 'greetings'],
            farewell: ['goodbye', 'bye', 'see you', 'farewell', 'take care', 'until next time', 'see you later'],
            question: ['what', 'why', 'how', 'when', 'where', 'who', 'which', 'can you', 'could you', 'would you'],
            compliment: ['beautiful', 'handsome', 'smart', 'intelligent', 'talented', 'skilled', 'impressive', 'remarkable'],
            gratitude: ['thank', 'thanks', 'grateful', 'appreciate', 'thankful', 'much obliged']
        };
        
        this.intensityModifiers = {
            high: ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'utterly', 'so', 'really'],
            medium: ['quite', 'pretty', 'fairly', 'rather', 'somewhat', 'moderately'],
            low: ['a bit', 'slightly', 'kind of', 'sort of', 'a little', 'mildly']
        };
        
        this.negationWords = ['not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere', 'hardly', 'scarcely', 'barely'];
        
        this.punctuationEmotions = {
            '!': { emotion: 'surprised', intensity: 0.3 },
            '!!!': { emotion: 'surprised', intensity: 0.8 },
            '?': { emotion: 'surprised', intensity: 0.2 },
            '???': { emotion: 'surprised', intensity: 0.6 },
            ':)': { emotion: 'happy', intensity: 0.6 },
            ':D': { emotion: 'happy', intensity: 0.8 },
            ':(': { emotion: 'sad', intensity: 0.6 },
            ':/': { emotion: 'disgusted', intensity: 0.4 },
            ':o': { emotion: 'surprised', intensity: 0.7 },
            'xD': { emotion: 'happy', intensity: 0.9 }
        };
    }
    
    analyze(text) {
        if (!text || typeof text !== 'string') {
            return this.createEmptyResult();
        }
        
        const cleanText = this.preprocessText(text);
        const words = this.tokenize(cleanText);
        
        const emotions = this.detectEmotions(words, cleanText);
        const context = this.detectContext(words, cleanText);
        const punctuationAnalysis = this.analyzePunctuation(text);
        const sentiment = this.calculateSentiment(emotions);
        const primaryEmotion = this.determinePrimaryEmotion(emotions, punctuationAnalysis);
        const confidence = this.calculateConfidence(emotions, context, punctuationAnalysis);
        
        return {
            text: text,
            primaryEmotion: primaryEmotion.emotion,
            intensity: primaryEmotion.intensity,
            confidence: confidence,
            sentiment: sentiment,
            context: context,
            emotions: emotions,
            punctuation: punctuationAnalysis,
            timestamp: Date.now()
        };
    }
    
    preprocessText(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s!?.:;,'"()-]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }
    
    tokenize(text) {
        return text.split(/\s+/).filter(word => word.length > 0);
    }
    
    detectEmotions(words, fullText) {
        const emotions = {
            happy: 0,
            sad: 0,
            angry: 0,
            surprised: 0,
            fearful: 0,
            disgusted: 0
        };
        
        Object.keys(this.emotionKeywords).forEach(emotion => {
            const keywords = this.emotionKeywords[emotion];
            
            keywords.primary.forEach(keyword => {
                if (fullText.includes(keyword)) {
                    emotions[emotion] += 1.0;
                }
            });
            
            keywords.secondary.forEach(keyword => {
                if (fullText.includes(keyword)) {
                    emotions[emotion] += 0.7;
                }
            });
            
            keywords.tertiary.forEach(keyword => {
                if (fullText.includes(keyword)) {
                    emotions[emotion] += 0.4;
                }
            });
        });
        
        this.applyIntensityModifiers(emotions, words, fullText);
        this.applyNegation(emotions, words, fullText);
        this.normalizeScores(emotions);
        
        return emotions;
    }
    
    applyIntensityModifiers(emotions, words, fullText) {
        Object.keys(this.intensityModifiers).forEach(level => {
            const modifiers = this.intensityModifiers[level];
            const multiplier = level === 'high' ? 1.5 : level === 'medium' ? 1.2 : 0.8;
            
            modifiers.forEach(modifier => {
                if (fullText.includes(modifier)) {
                    Object.keys(emotions).forEach(emotion => {
                        if (emotions[emotion] > 0) {
                            emotions[emotion] *= multiplier;
                        }
                    });
                }
            });
        });
    }
    
    applyNegation(emotions, words, fullText) {
        let negationFound = false;
        
        this.negationWords.forEach(negWord => {
            if (fullText.includes(negWord)) {
                negationFound = true;
            }
        });
        
        if (negationFound) {
            if (emotions.happy > 0) {
                emotions.sad += emotions.happy * 0.5;
                emotions.happy *= 0.3;
            }
            
            Object.keys(emotions).forEach(emotion => {
                if (emotion !== 'sad' && emotions[emotion] > 0) {
                    emotions[emotion] *= 0.7;
                }
            });
        }
    }
    
    normalizeScores(emotions) {
        const maxScore = Math.max(...Object.values(emotions));
        
        if (maxScore > 0) {
            Object.keys(emotions).forEach(emotion => {
                emotions[emotion] = Math.min(emotions[emotion] / maxScore, 1.0);
            });
        }
    }
    
    detectContext(words, fullText) {
        let maxScore = 0;
        let detectedContext = 'neutral';
        
        Object.keys(this.contextKeywords).forEach(context => {
            const keywords = this.contextKeywords[context];
            let score = 0;
            
            keywords.forEach(keyword => {
                if (fullText.includes(keyword)) {
                    score += 1;
                }
            });
            
            if (score > maxScore) {
                maxScore = score;
                detectedContext = context;
            }
        });
        
        if (fullText.includes('?')) {
            detectedContext = 'question';
        }
        
        if (fullText.includes('error') || fullText.includes('problem') || fullText.includes('wrong')) {
            detectedContext = 'error';
        }
        
        if (fullText.includes('success') || fullText.includes('completed') || fullText.includes('done')) {
            detectedContext = 'success';
        }
        
        return detectedContext;
    }
    
    analyzePunctuation(text) {
        const analysis = {
            exclamationCount: 0,
            questionCount: 0,
            emoticons: [],
            detectedEmotions: []
        };
        
        analysis.exclamationCount = (text.match(/!/g) || []).length;
        analysis.questionCount = (text.match(/\?/g) || []).length;
        
        Object.keys(this.punctuationEmotions).forEach(pattern => {
            if (text.includes(pattern)) {
                analysis.emoticons.push(pattern);
                analysis.detectedEmotions.push(this.punctuationEmotions[pattern]);
            }
        });
        
        return analysis;
    }
    
    calculateSentiment(emotions) {
        const positive = emotions.happy;
        const negative = emotions.sad + emotions.angry + emotions.fearful + emotions.disgusted;
        const neutral = 1 - positive - negative;
        
        let sentiment = 'neutral';
        let polarity = 0;
        
        if (positive > negative && positive > 0.3) {
            sentiment = 'positive';
            polarity = positive - negative;
        } else if (negative > positive && negative > 0.3) {
            sentiment = 'negative';
            polarity = negative - positive;
        }
        
        return {
            sentiment: sentiment,
            polarity: Math.max(-1, Math.min(1, polarity)),
            positive: positive,
            negative: negative,
            neutral: neutral
        };
    }
    
    determinePrimaryEmotion(emotions, punctuationAnalysis) {
        let primaryEmotion = 'neutral';
        let maxScore = 0;
        
        Object.keys(emotions).forEach(emotion => {
            if (emotions[emotion] > maxScore) {
                maxScore = emotions[emotion];
                primaryEmotion = emotion;
            }
        });
        
        punctuationAnalysis.detectedEmotions.forEach(puncEmotion => {
            if (puncEmotion.intensity > maxScore) {
                maxScore = puncEmotion.intensity;
                primaryEmotion = puncEmotion.emotion;
            }
        });
        
        let intensity = maxScore;
        
        if (punctuationAnalysis.exclamationCount > 0) {
            intensity = Math.min(intensity + (punctuationAnalysis.exclamationCount * 0.2), 1.0);
        }
        
        if (intensity < 0.1) {
            primaryEmotion = 'neutral';
            intensity = 0.5;
        }
        
        return {
            emotion: primaryEmotion,
            intensity: intensity
        };
    }
    
    calculateConfidence(emotions, context, punctuationAnalysis) {
        let confidence = 0;
        
        const maxEmotion = Math.max(...Object.values(emotions));
        confidence += maxEmotion * 0.5;
        
        if (context !== 'neutral') {
            confidence += 0.2;
        }
        
        if (punctuationAnalysis.emoticons.length > 0) {
            confidence += 0.3;
        }
        
        if (punctuationAnalysis.exclamationCount > 0 || punctuationAnalysis.questionCount > 0) {
            confidence += 0.1;
        }
        
        return Math.min(confidence, 1.0);
    }
    
    createEmptyResult() {
        return {
            text: '',
            primaryEmotion: 'neutral',
            intensity: 0.5,
            confidence: 0,
            sentiment: {
                sentiment: 'neutral',
                polarity: 0,
                positive: 0,
                negative: 0,
                neutral: 1
            },
            context: 'neutral',
            emotions: {
                happy: 0,
                sad: 0,
                angry: 0,
                surprised: 0,
                fearful: 0,
                disgusted: 0
            },
            punctuation: {
                exclamationCount: 0,
                questionCount: 0,
                emoticons: [],
                detectedEmotions: []
            },
            timestamp: Date.now()
        };
    }
    
    analyzeBatch(texts) {
        return texts.map(text => this.analyze(text));
    }
    
    getEmotionSuggestions(context) {
        const suggestions = {
            greeting: ['happy', 'neutral'],
            farewell: ['sad', 'neutral'],
            question: ['surprised', 'neutral'],
            error: ['sad', 'angry'],
            success: ['happy'],
            compliment: ['happy'],
            gratitude: ['happy', 'neutral']
        };
        
        return suggestions[context] || ['neutral'];
    }
    
    addEmotionKeywords(emotion, keywords) {
        if (this.emotionKeywords[emotion]) {
            if (!this.emotionKeywords[emotion].custom) {
                this.emotionKeywords[emotion].custom = [];
            }
            this.emotionKeywords[emotion].custom.push(...keywords);
        }
    }
    
    getStatistics(analyses) {
        if (!analyses || analyses.length === 0) {
            return {};
        }
        
        const stats = {
            totalAnalyses: analyses.length,
            averageConfidence: 0,
            emotionDistribution: {},
            contextDistribution: {},
            sentimentDistribution: { positive: 0, negative: 0, neutral: 0 }
        };
        
        analyses.forEach(analysis => {
            stats.averageConfidence += analysis.confidence;
            
            if (!stats.emotionDistribution[analysis.primaryEmotion]) {
                stats.emotionDistribution[analysis.primaryEmotion] = 0;
            }
            stats.emotionDistribution[analysis.primaryEmotion]++;
            
            if (!stats.contextDistribution[analysis.context]) {
                stats.contextDistribution[analysis.context] = 0;
            }
            stats.contextDistribution[analysis.context]++;
            
            stats.sentimentDistribution[analysis.sentiment.sentiment]++;
        });
        
        stats.averageConfidence /= analyses.length;
        
        return stats;
    }
    
    exportConfig() {
        return {
            emotionKeywords: this.emotionKeywords,
            contextKeywords: this.contextKeywords,
            intensityModifiers: this.intensityModifiers,
            negationWords: this.negationWords,
            punctuationEmotions: this.punctuationEmotions,
            version: '1.0.0',
            exportDate: new Date().toISOString()
        };
    }
    
    importConfig(config) {
        if (config.emotionKeywords) {
            this.emotionKeywords = { ...this.emotionKeywords, ...config.emotionKeywords };
        }
        if (config.contextKeywords) {
            this.contextKeywords = { ...this.contextKeywords, ...config.contextKeywords };
        }
        if (config.intensityModifiers) {
            this.intensityModifiers = { ...this.intensityModifiers, ...config.intensityModifiers };
        }
        if (config.negationWords) {
            this.negationWords = [...this.negationWords, ...config.negationWords];
        }
        if (config.punctuationEmotions) {
            this.punctuationEmotions = { ...this.punctuationEmotions, ...config.punctuationEmotions };
        }
        
        console.log('Emotion analyzer configuration imported');
    }
}