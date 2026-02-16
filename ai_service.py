import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API
# Note: In a production environment, the API key should be set in a .env file
API_KEY = os.getenv("GEMINI_API_KEY")

class GenerativeAIService:
    @staticmethod
    def generate_curriculum(career_goal, weak_subjects, weeks=8, hours_per_day=2.0):
        """
        Generates a structured curriculum JSON using Google's Gemini AI.
        """
        if not API_KEY:
            print("WARNING: GEMINI_API_KEY not found. Using Mock AI generator.")
            return GenerativeAIService._mock_ai_generate(career_goal, weak_subjects, weeks, hours_per_day)

        try:
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are an expert educational consultant. Generate a highly personalized learning curriculum for a student pursuing a career as a '{career_goal}'.
            
            Student Constraints:
            - Weak Subjects: {weak_subjects}
            - Duration: {weeks} weeks
            - Available time: {hours_per_day} hours per day
            
            Return ONLY a JSON array of objects. Each object represents a topic and must have exactly these keys:
            - topic: (string) name of the topic
            - difficulty_level: (string: "Easy", "Medium", or "Hard")
            - estimated_hours: (integer) hours to master
            - week_number: (integer) which week to study this
            - subtopics: (array of strings) 3-4 specific concepts within this topic
            
            The JSON should be valid and follow the student constraints. PRIORITIZE weak subjects in the first few weeks.
            Ensure the total hours fit within the available {weeks * 7 * hours_per_day} total hours.
            """
            
            response = model.generate_content(prompt)
            # Find the JSON block in the response
            text = response.text
            start = text.find('[')
            end = text.rfind(']') + 1
            
            if start != -1 and end != -1:
                curriculum_json = text[start:end]
                return json.loads(curriculum_json)
            else:
                raise Exception("Could not find valid JSON in AI response")
                
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return GenerativeAIService._mock_ai_generate(career_goal, weak_subjects, weeks, hours_per_day)

    @staticmethod
    def _mock_ai_generate(career_goal, weak_subjects, weeks=8, hours_per_day=2.0):
        """
        An advanced fallback generator that provides highly detailed roadmaps 
        even without a Gemini API key.
        """
        print(f"Generating optimized roadmap for: {career_goal}")
        
        # Normalize goal
        goal = career_goal.lower()
        
        # Pre-defined career path templates
        paths = {
            "software": [
                ("Frontend Fundamentals", ["HTML5 Semantic Tags", "CSS3 Flexbox & Grid", "Modern JavaScript (ES6+)", "Responsive Design"]),
                ("Frontend Frameworks", ["React Hooks & Component Lifecycle", "State Management (Redux/Zustand)", "API Integration with Axios", "Unit Testing basics"]),
                ("Backend & Node.js", ["Node.js Runtime & NPM", "Express.js Routing", "RESTful API Design", "Authentication (JWT/OAuth)"]),
                ("Databases & Logic", ["SQL vs NoSQL Architecture", "MongoDB/PostgreSQL basics", "Schema Design & Normalization", "Query Optimization"]),
                ("DevOps & Version Control", ["Git Workflow (Gitflow)", "Docker Containerization", "CI/CD Pipelines", "Cloud Deployment basics"]),
                ("System Design", ["Scalability & Load Balancing", "Caching Strategies", "Microservices vs Monolith", "Security Best Practices"])
            ],
            "data": [
                ("Python for Data Science", ["NumPy & Pandas basics", "Data Cleaning Techniques", "Jupyter Notebooks", "Virtual Environments"]),
                ("Statistics & Mathematics", ["Descriptive Statistics", "Probability Theory", "Linear Algebra for ML", "Hypothesis Testing"]),
                ("Data Visualization", ["Matplotlib & Seaborn", "Tableau/PowerBI basics", "Storytelling with Data", "Interactive Dashboards"]),
                ("Machine Learning Core", ["Linear & Logistic Regression", "Decision Trees & Random Forests", "Cross-Validation Techniques", "Model Evaluation Metrics"]),
                ("Advanced ML & AI", ["Neural Networks & Deep Learning", "NLP (Natural Language Processing)", "Computer Vision fundamentals", "MLOps & Model Deployment"]),
                ("Big Data Systems", ["SQL for Data Analysis", "Spark & Hadoop introduction", "Data Warehousing (Snowflake/BigQuery)", "Cloud Data Services"])
            ],
            "design": [
                ("Design Thinking & UI basics", ["Typography & Color Theory", "Grid Systems & Layouts", "Accessibility (WCAG)", "Design Systems introduction"]),
                ("Prototyping Tools", ["Figma Advanced Mastery", "Interactive Components", "Auto-layout & Variables", "Design-to-Code handoff"]),
                ("UX Research", ["User Personas & Journey Mapping", "Usability Testing", "Information Architecture", "Wireframing basics"]),
                ("Visual Communication", ["Iconography & Illustrations", "Micro-interactions", "Motion Design", "Branding & Identity"]),
                ("Product Management", ["Agile Design Process", "Stakeholder Communication", "Portfolio Development", "Design Ethics"]),
                ("Frontend for Designers", ["Basic HTML/CSS", "Design frameworks (Tailwind/Bootstrap)", "Animation Libraries", "Collaborative workflows"])
            ]
        }

        # Select the best matching path or use a generic one
        selected_path = []
        if "software" in goal or "developer" in goal or "engineer" in goal:
            selected_path = paths["software"]
        elif "data" in goal or "ai" in goal or "machine" in goal:
            selected_path = paths["data"]
        elif "design" in goal or "ui" in goal or "ux" in goal:
            selected_path = paths["design"]
        else:
            # Generic catch-all path
            selected_path = [
                (f"Introduction to {career_goal}", ["Core Concepts", "Industry Overview", "Essential Terminology", "Key Tools"]),
                ("Foundational Skills", ["Basic Workflow", "Environment Setup", "Primary Techniques", "Standard Best Practices"]),
                ("Intermediate Concepts", ["Problem Solving", "Collaboration", "Process Optimization", "Real-world Application"]),
                ("Advanced Topics", ["Expert Methods", "Specialized Sub-fields", "Integration", "Strategic Planning"]),
                ("Project & Portfolio", ["Case Studies", "Capstones", "Documentation", "Presentation"]),
                ("Mastery & Future Trends", ["Industry Innovation", "Next-gen Tech", "Continuous Learning", "Career Roadmap"])
            ]

        # Inject weak subjects into the first 2 weeks
        if weak_subjects:
            weaks = [w.strip() for w in weak_subjects.split(',')]
            for i, w in enumerate(weaks[:2]):
                if i < len(selected_path):
                    original_topic, subtopics = selected_path[i]
                    selected_path[i] = (f"{original_topic} (Focus: {w})", [f"Fundamental {w} concepts"] + subtopics[:3])

        # Distribute topics across the requested weeks
        curriculum = []
        total_topics = len(selected_path)
        
        # Randomize the path order slightly to feel more "AI" (keeping foundational logic)
        # We'll keep the first week foundational but shuffle the middle ones
        if total_topics > 3:
            middle = selected_path[1:-1]
            random.shuffle(middle)
            selected_path = [selected_path[0]] + middle + [selected_path[-1]]

        for i in range(weeks):
            # Pick a topic from the template (cycling if weeks > original topics)
            topic_idx = int((i * total_topics) / weeks) % total_topics
            orig_topic, orig_subs = selected_path[topic_idx]
            
            # Randomly shuffle subtopics for variety
            current_subs = list(orig_subs)
            random.shuffle(current_subs)
            
            # Add a slight variation to the topic name if it's a repeat week
            display_topic = orig_topic
            if i >= total_topics:
                prefixes = ["Advanced", "Deep Dive into", "Practical", "Mastering"]
                display_topic = f"{random.choice(prefixes)} {orig_topic}"

            curriculum.append({
                "topic": display_topic,
                "difficulty_level": "Easy" if i < weeks/3 else ("Medium" if i < 2*weeks/3 else "Hard"),
                "estimated_hours": hours_per_day * 5, # Assume 5 study days a week
                "week_number": i + 1,
                "subtopics": current_subs[:4]
            })

        return curriculum
