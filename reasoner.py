# reasoner.py
import re
import json
import os
import subprocess
from datetime import datetime
from coder import Coder
from project_manager import ProjectManager

class Reasoner:
    def deduplicate_recommendations(self, text):
        """Remove duplicate lines from recommendations"""
        if not text:
            return text
        
        lines = text.split('\n')
        seen = set()
        unique_lines = []
        
        for line in lines:
            clean_line = line.strip()
            if clean_line and clean_line not in seen:
                seen.add(clean_line)
                unique_lines.append(line)
        
        return '\n'.join(unique_lines) 
    def format_security_report(self, assessment, risk_level, recommendations, fix_code=None):
        """Format the security report in a professional, structured way"""
        
        # Create a clean header
        report = [
            "🔒 SECURITY ASSESSMENT REPORT",
            "=" * 50,
            f"Risk Level: {risk_level}",
            ""
        ]
        
        # Add assessment section
        report.extend([
            "📋 ASSESSMENT:",
            "-" * 30,
            assessment,
            ""
        ])
        
        # Add recommendations section
        if recommendations and recommendations != "No recommendations":
            report.extend([
                "💡 RECOMMENDATIONS:",
                "-" * 30,
                recommendations,
                ""
            ])
        
        # Add automated fixes section if available
        if fix_code:
            report.extend([
                "⚡ AUTOMATED FIXES:",
                "-" * 30,
                "The following code can implement these recommendations:",
                "",
                fix_code,
                ""
            ])
        
        # Add next steps
        report.extend([
            "🚀 NEXT STEPS:",
            "-" * 30,
            "1. Review the assessment above",
            "2. Implement the recommended fixes",
            "3. Run security scans to verify improvements",
            "4. Consider implementing continuous security monitoring"
        ])
        
        return "\n".join(report)
    def __init__(self, deepseek_client):
        self.client = deepseek_client
        self.coder = Coder(deepseek_client)
        self.project_manager = None
        self.current_context = ""
        self.current_project_path = None
        self.ambiguous_paths = []
        self.waiting_for_path_selection = False
        self.original_request = ""
        self.security_tools = {
            'Python': ['bandit', 'safety', 'pylint'],
            'JavaScript': ['npm audit', 'eslint', 'snyk'],
            'Java': ['spotbugs', 'dependency-check'],
            'Go': ['gosec', 'staticcheck'],
            'Ruby': ['brakeman', 'bundler-audit'],
            'PHP': ['phpcs', 'phpmd'],
            'C#': ['security-code-scan'],
            'C/C++': ['cppcheck', 'flawfinder']
        }

    def extract_path(self, user_input):
        """
        Enhanced path extraction that handles various path formats and detects ambiguities.
        """
        # Look for explicit path patterns first
        path_patterns = [
            r'\/[^\s]*\/[^\s]*',  # Unix paths
            r'[A-Za-z]:\\[^\\s]*',  # Windows paths
            r'project[\\s][^\\s]*',  # "project my-app"
            r'directory[\\s][^\\s]*',  # "directory /path/to/project"
            r'path[\\s][^\\s]*',  # "path /to/project"
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, user_input)
            if match:
                path = match.group(0)
                # Clean up the path
                path = path.replace("project ", "").replace("directory ", "").replace("path ", "")
                return path
        
        # If no explicit path found, look for standalone words that might be directory names
        words = user_input.split()
        potential_paths = set()  # Use a set to avoid duplicates
        
        for word in words:
            # Skip common words that are unlikely to be paths
            if word.lower() in ["analyze", "scan", "review", "check", "project", "directory", 
                              "path", "for", "the", "a", "an", "security", "issues", "1", "2", "3", "4", "5"]:
                continue
            
            # Check if this could be a relative path
            if os.path.exists(word) and os.path.isdir(word):
                potential_paths.add(os.path.abspath(word))
            
            # Check if it's a relative path from current directory
            potential_path = os.path.join(os.getcwd(), word)
            if os.path.exists(potential_path) and os.path.isdir(potential_path):
                potential_paths.add(os.path.abspath(potential_path))
        
        # Convert set to list
        potential_paths = list(potential_paths)
        
        # Handle ambiguous cases
        if len(potential_paths) == 0:
            return None
        elif len(potential_paths) == 1:
            return potential_paths[0]
        else:
            # Multiple possibilities found - store them for disambiguation
            self.ambiguous_paths = potential_paths
            return "AMBIGUOUS"

    def handle_path_selection(self, user_input):
        """
        Handle the user's selection from ambiguous paths
        """
        try:
            # Try to parse the selection as a number
            selection = int(user_input.strip()) - 1  # Convert to 0-based index
            
            if 0 <= selection < len(self.ambiguous_paths):
                selected_path = self.ambiguous_paths[selection]
                self.ambiguous_paths = []  # Clear the ambiguous paths
                self.waiting_for_path_selection = False
                return selected_path
            else:
                return "QUESTION: Invalid selection. Please choose a number from the list."
        except ValueError:
            # If it's not a number, check if it's a path
            if os.path.exists(user_input) and os.path.isdir(user_input):
                self.ambiguous_paths = []
                self.waiting_for_path_selection = False
                return user_input
            else:
                return "QUESTION: Please enter a valid number from the list or provide a full path."

    def run_language_specific_scans(self, languages):
        """
        Run language-specific security tools based on detected languages
        """
        results = {}
        
        for language in languages:
            if language in self.security_tools:
                print(f"[Reasoner] Running language-specific scans for {language}...")
                tools = self.security_tools[language]
                
                for tool in tools:
                    try:
                        # This is a placeholder - you'd implement actual tool execution
                        results[f"{language}_{tool}"] = f"Would run {tool} scan"
                    except Exception as e:
                        results[f"{language}_{tool}"] = f"Error running {tool}: {str(e)}"
        
        return results

    def generate_fix_code(self, recommendations):
        """
        Generate code to implement the security recommendations
        """
        if not recommendations or recommendations == "No recommendations":
            return None
        
        prompt = f"""
        Based on the following security recommendations, generate Python code or shell commands to implement these fixes.
        Focus on actionable code that can be run to address the issues.

        RECOMMENDATIONS:
        {recommendations}

        Generate code that:
        1. Updates dependency files (like requirements.txt)
        2. Runs security scanning tools
        3. Fixes configuration issues
        4. Implements any other actionable recommendations

        Provide the code in a format that can be easily executed.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Reasoner] Error generating fix code: {e}")
            return None

    def analyze(self, user_input):
        """
        The enhanced Reasoner with comprehensive project analysis and fix generation capabilities.
        """
        print(f"[Reasoner] Analyzing input: '{user_input}'")
        
        # Check if we're waiting for a path selection
        if self.waiting_for_path_selection:
            path_result = self.handle_path_selection(user_input)
            if path_result.startswith("QUESTION:"):
                return path_result
            else:
                # We have a selected path, process the original request with this path
                self.current_project_path = path_result
                return self.analyze(self.original_request)
        
        # Store the original request for potential disambiguation
        self.original_request = user_input
        
        # Check if this is a project-related request
        project_keywords = ["project", "directory", "file", "scan", "audit", "fix", 
                           "vulnerability", "review", "analyze", "check", "security"]
        is_project_request = any(keyword in user_input.lower() for keyword in project_keywords)
        
        # Try to extract a path from the input
        project_path = self.extract_path(user_input)
        
        # Handle ambiguous paths
        if project_path == "AMBIGUOUS":
            self.waiting_for_path_selection = True
            paths_list = "\n".join([f"{i+1}. {path}" for i, path in enumerate(self.ambiguous_paths)])
            return f"QUESTION: I found multiple directories with that name. Which one did you mean?\n{paths_list}\nPlease enter the number:"
        
        if is_project_request or project_path:
            if project_path:
                # Validate the path exists
                if not os.path.exists(project_path) or not os.path.isdir(project_path):
                    return f"QUESTION: The path '{project_path}' doesn't exist or is not a directory. Please provide a valid path."
                
                self.current_project_path = project_path
                self.project_manager = ProjectManager(project_path)
                
                # Run comprehensive automated scans
                print("[Reasoner] Running comprehensive project analysis...")
                scan_results = self.project_manager.run_scan()
                audit_results = self.project_manager.run_audit()
                
                # Run language-specific scans if languages are detected
                language_specific_results = {}
                if 'languages_detected' in scan_results and scan_results['languages_detected']:
                    languages = list(scan_results['languages_detected'].keys())
                    language_specific_results = self.run_language_specific_scans(languages)
                
                # Prepare comprehensive context for AI analysis
                self.current_context = f"""
                USER REQUEST: {user_input}
                PROJECT SCAN RESULTS: {json.dumps(scan_results, indent=2)}
                VULNERABILITY AUDIT RESULTS: {json.dumps(audit_results, indent=2)}
                LANGUAGE SPECIFIC SCANS: {json.dumps(language_specific_results, indent=2)}
                """
                
                # Ask AI to analyze the situation and decide next steps
                analysis_prompt = f"""
                Analyze this software project comprehensively and provide a detailed security assessment.

                {self.current_context}

                Based on this comprehensive analysis, you must:
                1. Identify any security vulnerabilities or issues
                2. Assess the overall code quality and security posture
                3. Recommend specific fixes or improvements
                4. Provide a security risk rating (High/Medium/Low)
                5. Suggest appropriate security tools to run based on the project's tech stack

                If the analysis results are empty or incomplete, suggest better scanning approaches.
                If you can provide a comprehensive assessment, do so.
                If critical information is missing, ask precise, targeted questions.

                Respond in this exact format:
                ASSESSMENT: [Comprehensive security assessment]
                RISK_LEVEL: [High/Medium/Low]
                RECOMMENDATIONS: [Specific recommendations]
                QUESTIONS: [Any remaining questions or null if none]
                """
                
                # Get the AI's analysis
                analysis_response = self.client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    temperature=0.1
                )
                decision = analysis_response.choices[0].message.content.strip()
                print(f"[Reasoner] Decision: {decision}")
                
                # Process the comprehensive assessment with improved regex patterns
                assessment_match = re.search(r"ASSESSMENT:\s*(.*?)(?=RISK_LEVEL:|\Z)", decision, re.DOTALL)
                risk_match = re.search(r"RISK_LEVEL:\s*(.*?)(?=RECOMMENDATIONS:|\Z)", decision, re.DOTALL)
                recommendations_match = re.search(r"RECOMMENDATIONS:\s*(.*?)(?=QUESTIONS:|\Z)", decision, re.DOTALL)
                questions_match = re.search(r"QUESTIONS:\s*(.*)$", decision, re.DOTALL)
                
                assessment = assessment_match.group(1).strip() if assessment_match else "No assessment provided"
                risk_level = risk_match.group(1).strip() if risk_match else "Unknown"
                recommendations = recommendations_match.group(1).strip() if recommendations_match else "No recommendations"
                questions = questions_match.group(1).strip() if questions_match else "null"
                
                # Generate code to implement the recommendations
                fix_code = self.generate_fix_code(recommendations) if recommendations != "No recommendations" else None
                
                # Format the final response
                final_response = f"""
SECURITY ASSESSMENT REPORT
==========================
Risk Level: {risk_level}

Assessment:
{assessment}

Recommendations:
{recommendations}
"""
                # Add fix code if available
                if fix_code:
                    final_response += f"""

AUTOMATED FIXES:
================
Here's code to implement the recommendations:

{fix_code}
"""
                
                # If there are follow-up questions, add them
                if questions != "null":
                    return f"QUESTION: {questions}\n\n{final_response}"
                else:
                    return final_response
            
            else:
                # No path found, ask for it
                return "QUESTION: Please provide the path to the project you want me to analyze."
        
        else:
            # For non-project requests, use the standard analysis
            analysis_prompt = f"""
            Analyze the following user request for a coding task. Your job is to decide if it has enough specific details to write code immediately.

            USER REQUEST: "{user_input}"

            If the request is VAGUE or MISSING critical details (like target programming language, framework, key functionality, or specific parameters), respond with a single, clear follow-up question asking for the most important missing piece of information.
            If the request is COMPLETE and ACTIONABLE, respond with the word: "CODE_GENERATION_APPROVED".

            Respond only with the follow-up question or "CODE_GENERATION_APPROVED".
            """

            # Get the Reasoner's decision from the AI
            analysis_response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1
            )
            decision = analysis_response.choices[0].message.content.strip()
            print(f"[Reasoner] Decision: {decision}")

            # Process the decision
            if decision == "CODE_GENERATION_APPROVED":
                # For standard requests, optimize the prompt before sending to Coder
                print("[Reasoner] Request complete. Optimizing prompt for Coder.")
                
                optimization_prompt = f"""
                The following user request has been approved for code generation. Your job is to rewrite it into a clear, concise, and highly effective prompt for an AI code generator.

                Original User Request: "{user_input}"

                Instructions for optimization:
                1. Remove any greetings, filler words, or vague phrases.
                2. Make it an imperative command (e.g., "Write a Python function...").
                3. Specify the programming language if it's implied but not stated.
                4. Add key details like input parameters and return values if missing.
                5. Make it as short as possible while being unambiguous.

                Respond only with the optimized prompt.
                """

                optimized_response = self.client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=[{"role": "user", "content": optimization_prompt}],
                    temperature=0.1
                )
                optimized_prompt = optimized_response.choices[0].message.content.strip()
                
                print(f"[Reasoner] Optimized Prompt: {optimized_prompt}")
                generated_code = self.coder.generate_code(optimized_prompt)
                return generated_code
            else:
                # If not approved, return the follow-up question
                print("[Reasoner] Request incomplete. Question generated.")
                return f"QUESTION: {decision}"