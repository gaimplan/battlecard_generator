import json
from datetime import datetime
import os
import sys

# Add root directory to Python path to import run.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from run import PRODUCT_NAME

def load_json_file(file_path: str) -> dict:
    """Load a JSON file and return its contents."""
    with open(file_path, 'r') as f:
        return json.load(f)

def format_strategic_overview(overview: dict, sources_list: list) -> str:
    """Format strategic overview section and collect sources."""
    md = "# Strategic Overview\n\n"
    if 'strategic_overview' in overview and isinstance(overview['strategic_overview'], dict):
        inner = overview['strategic_overview']
        if 'elevator_pitch' in inner:
            md += f"**Elevator Pitch:** {inner['elevator_pitch']}\n\n"
        if 'target_customer_profile' in inner:
            md += "**Target Customer Profile:**\n"
            if 'personas' in inner['target_customer_profile']:
                for persona in inner['target_customer_profile']['personas']:
                    md += f"- **{persona['role']}**\n"
                    md += f"  - **Key Goal:** {persona['key_goal']}\n"
                    md += "  - **Pain Points:**\n"
                    for point in persona['pain_points']:
                        md += f"    - {point}\n"
            if 'primary_pain_point' in inner['target_customer_profile']:
                md += f"\n**Primary Pain Point:** {inner['target_customer_profile']['primary_pain_point']}\n\n"
        if 'market_context' in inner:
            md += f"**Market Context:** {inner['market_context']}\n"
    if 'sources' in overview:
        sources_list.extend(overview['sources'])
    return md

def format_value_propositions(propositions: dict, sources_list: list) -> str:
    """Format value propositions section and collect sources."""
    md = "# Value Propositions\n\n"
    if 'value_propositions' in propositions and isinstance(propositions['value_propositions'], list):
        for prop in propositions['value_propositions']:
            md += f"## {prop.get('headline', 'Untitled')}\n\n"
            if 'key_benefits' in prop:
                md += "**Key Benefits:**\n"
                for benefit in prop['key_benefits']:
                    md += f"- {benefit}\n"
                md += "\n"
            if 'supporting_features' in prop:
                md += "**Supporting Features:**\n"
                for feature in prop['supporting_features']:
                    md += f"- {feature}\n"
                md += "\n"
    if 'sources' in propositions:
        sources_list.extend(propositions['sources'])
    return md

def format_qualifying_questions(questions: list, sources_list: list) -> str:
    """Format qualifying questions section and collect sources."""
    md = "# Qualifying Questions\n\n"
    for topic in questions:
        md += f"## {topic.get('topic', 'Untitled Topic')}\n\n"
        for section in topic.get('sections', []):
            md += f"### {section.get('section_name', 'Untitled Section')}\n\n"
            for statement in section.get('statements', []):
                md += f"- {statement.get('statement', '')}\n"
            md += "\n"
    if isinstance(questions, dict) and 'sources' in questions:
        sources_list.extend(questions['sources'])
    return md

def format_use_cases(use_cases: list, sources_list: list) -> str:
    """Format use cases section and collect sources."""
    md = "# Use Cases\n\n"
    for topic in use_cases:
        md += f"## {topic.get('topic', 'Untitled Topic')}\n\n"
        for use_case in topic.get('use_cases', []):
            md += f"### {use_case.get('title', 'Untitled')}\n\n"
            if 'problem_challenge' in use_case:
                md += "**Problem/Challenge:**\n"
                for stmt in use_case['problem_challenge']:
                    md += f"- {stmt.get('statement', '')}\n"
                md += "\n"
            if 'solution' in use_case:
                md += "**Solution:**\n"
                for stmt in use_case['solution']:
                    md += f"- {stmt.get('statement', '')}\n"
                md += "\n"
            if 'value_realized' in use_case:
                md += "**Value Realized:**\n"
                for stmt in use_case['value_realized']:
                    md += f"- {stmt.get('statement', '')}\n"
                md += "\n"
    if isinstance(use_cases, dict) and 'sources' in use_cases:
        sources_list.extend(use_cases['sources'])
    return md

def format_competitive_analysis(competitive: dict, sources_list: list) -> str:
    """Format competitive analysis section dynamically and collect sources."""
    md = "# Competitive Analysis\n\n"
    
    # Handle positioning sections dynamically
    for key in competitive.keys():
        if key.startswith('positioning_vs_'):
            # Extract competitor name from the key (e.g., "positioning_vs_zoom one" -> "Zoom One")
            competitor = key.replace('positioning_vs_', '').replace('_', ' ').title()
            md += f"## Positioning vs {competitor}\n\n"
            md += f"{competitive[key].get('statement', '')}\n\n"
            if 'advantages' in competitive[key]:
                md += "**Advantages:**\n"
                for adv in competitive[key]['advantages']:
                    md += f"- {adv.get('statement', '')}\n"
                md += "\n"
    
    # Handle competitive matrix dynamically
    if 'competitive_matrix' in competitive:
        md += "## Competitive Matrix\n\n"
        # Get all unique product names from the scores across all features
        products = set()
        for feature in competitive['competitive_matrix']:
            for score in feature.get('scores', []):
                products.add(score.get('product', ''))
        products = sorted(products)  # Sort for consistent ordering
        
        # Build table header
        md += "| Feature | " + " | ".join(products) + " |\n"
        md += "|---------|" + "--------|" * len(products) + "\n"
        
        # Build table rows
        for feature in competitive['competitive_matrix']:
            row = f"| {feature.get('feature', 'Unnamed Feature')} |"
            scores = {score['product']: score for score in feature.get('scores', [])}
            for product in products:
                if product in scores:
                    score = scores[product]
                    row += f" {score.get('score', '-')}<br>{score.get('justification', '')} |"
                else:
                    row += " - |"
            md += row + "\n"
        md += "\n"
    
    # Handle win themes
    if 'win_themes' in competitive:
        md += "## Win Themes\n\n"
        for theme in competitive['win_themes']:
            md += f"- {theme.get('statement', '')}\n"
        md += "\n"
    
    # Collect sources
    if 'sources' in competitive:
        sources_list.extend(competitive['sources'])
    
    return md

def format_objection_handling(objections: dict, sources_list: list) -> str:
    """Format objection handling section and collect sources."""
    md = "# Objection Handling\n\n"
    if 'objections' in objections:
        for objection in objections['objections']:
            md += f"## {objection.get('objection_name', 'Untitled Objection')}\n\n"
            if 'response' in objection:
                md += "**Response:**\n"
                for resp in objection['response']:
                    md += f"- {resp}\n"
                md += "\n"
            if 'evidence' in objection:
                md += "**Evidence:**\n"
                for ev in objection['evidence']:
                    md += f"- {ev}\n"
                md += "\n"
    if 'sources' in objections:
        sources_list.extend(objections['sources'])
    return md

def format_action_plan(plan: dict, sources_list: list) -> str:
    """Format action plan section and collect sources."""
    md = "# Action Plan\n\n"
    if 'action_plan' in plan:
        inner = plan['action_plan']
        if 'value_that_closes' in inner:
            md += "## Value That Closes\n\n"
            for value in inner['value_that_closes']:
                md += f"- {value}\n"
            md += "\n"
        if 'next_steps' in inner:
            md += "## Next Steps\n\n"
            for step in inner['next_steps']:
                md += f"- {step}\n"
            md += "\n"
        if 'sales_playbook' in inner:
            md += "## Sales Playbook\n\n"
            for play in inner['sales_playbook']:
                md += f"- {play}\n"
            md += "\n"
    if 'sources' in plan:
        sources_list.extend(plan['sources'])
    return md

def format_sources(sources_list: list) -> str:
    """Format the collected sources into a Sources section."""
    if not sources_list:
        return ""
    
    # Deduplicate sources based on title and url
    unique_sources = {}
    for source in sources_list:
        key = (source.get('title', ''), source.get('url', ''))
        unique_sources[key] = source
    
    md = "# Sources\n\n"
    for source in unique_sources.values():
        title = source.get('title', 'Untitled')
        url = source.get('url', 'No URL provided')
        md += f"- [{title}]({url})\n"
    return md

def convert_json_to_markdown():
    # Load the JSON data from output directory
    data = load_json_file('output/battlecard.json')
    battlecard = data['battlecard']

    # Collect all sources
    all_sources = []

    # Generate markdown content
    markdown_content = f"""# {PRODUCT_NAME} Battlecard
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    # Add each section and collect sources
    sections = [
        (format_strategic_overview, 'strategic_overview'),
        (format_value_propositions, 'value_propositions'),
        (format_qualifying_questions, 'qualifying_questions'),
        (format_use_cases, 'use_cases'),
        (format_competitive_analysis, 'competitive_analysis'),
        (format_objection_handling, 'objection_handling'),
        (format_action_plan, 'action_plan')
    ]

    for formatter, key in sections:
        if key in battlecard and battlecard[key]:
            markdown_content += formatter(battlecard[key], all_sources)
            markdown_content += "\n"

    # Append the Sources section
    markdown_content += format_sources(all_sources)

    # Write to file in output directory
    output_file = os.path.join('output', 'battlecard.md')
    with open(output_file, 'w') as f:
        f.write(markdown_content)
    
    print(f"Successfully converted battlecard.json to {output_file}")

if __name__ == "__main__":
    convert_json_to_markdown()