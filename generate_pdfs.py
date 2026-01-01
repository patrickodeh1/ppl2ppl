#!/usr/bin/env python
"""
Generate proper training PDFs with actual content.
This script creates PDFs for all training modules based on their titles and module content.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# PDF content mapping by module title
PDF_CONTENT = {
    "Mission Overview": {
        "subtitle": "Understanding Our Core Mission",
        "content": [
            "Our organization is dedicated to facilitating meaningful conversations and building genuine relationships with the communities we serve. The mission goes beyond transactional interactions—it's about establishing trust, understanding needs, and providing solutions that create lasting impact.",
            
            "Key Mission Elements:",
            "• Authentic Engagement: Build real relationships based on transparency and honesty",
            "• Community Impact: Focus on creating positive outcomes that benefit individuals and organizations",
            "• Professional Excellence: Maintain the highest standards of professionalism in all interactions",
            "• Continuous Improvement: Learn from feedback and continuously refine our approach",
            
            "As team members, you are the face of our organization. Every interaction you have represents our commitment to excellence and our dedication to making a difference. Understanding and embodying this mission is fundamental to your success in this role.",
        ]
    },
    "Petition Document Overview": {
        "subtitle": "Understanding the Petition Process",
        "content": [
            "A petition is the foundational document that initiates the relationship-building process with prospective supporters. It serves multiple purposes: establishing credibility, demonstrating commitment, and creating a formal record of intent.",
            
            "Components of an Effective Petition:",
            "• Title Section: Clear, compelling headline that explains the purpose",
            "• Background Information: Context that helps the reader understand the significance",
            "• Call to Action: Clear explanation of what supporters are being asked to do",
            "• Signature Lines: Professional format for documentation",
            
            "Best Practices:",
            "• Keep language clear and accessible to diverse audiences",
            "• Organize information in logical sections",
            "• Use professional formatting and appearance",
            "• Ensure all required information is included",
            "• Make the purpose immediately obvious to readers",
            
            "Remember: The petition is often the first impression potential supporters have of our initiative. Taking time to ensure it's well-presented demonstrates respect for their time and attention.",
        ]
    },
    "Ethical Engagement Guide": {
        "subtitle": "Professional and Honest Interactions",
        "content": [
            "Ethical engagement is the cornerstone of sustainable relationships. This guide outlines the principles and practices that define how we interact with supporters and the general public.",
            
            "Core Principles of Ethical Engagement:",
            "• Transparency: Always be honest about what you're asking and why",
            "• Respect: Treat every person with dignity regardless of their response",
            "• Honesty: Provide accurate information and correct misunderstandings",
            "• Integrity: Let your actions match your words",
            
            "Common Ethical Scenarios:",
            "1. When someone has questions: Answer honestly or offer to find accurate information",
            "2. When someone disagrees: Listen respectfully and avoid becoming defensive",
            "3. When you make a mistake: Acknowledge it immediately and correct it",
            "4. When pressured to bend the truth: Politely but firmly stick to facts",
            
            "Remember: Building trust takes time and consistency. One ethical lapse can damage relationships that took months to build. Your integrity is your most valuable asset in this role.",
        ]
    },
    "Field Gear Checklist": {
        "subtitle": "Essential Equipment for Successful Outreach",
        "content": [
            "Being properly prepared for field work is essential for success. This checklist ensures you have everything needed for productive, professional interactions.",
            
            "Must-Have Items:",
            "□ Petitions (sufficient quantity for your route)",
            "□ Pens (multiple, different colors for notes)",
            "□ Clipboard or folder (secure, professional appearance)",
            "□ Personal identification and credentials",
            "□ Contact information for support staff",
            "□ Water bottle (stay hydrated during long sessions)",
            "□ Weather-appropriate clothing and accessories",
            "□ Phone with charged battery",
            
            "Recommended Items:",
            "□ Hand sanitizer",
            "□ Small first aid kit",
            "□ Umbrella or rain protection",
            "□ Comfortable, supportive shoes",
            "□ Notebook for detailed notes",
            "□ Reference materials for common questions",
            
            "Pre-Shift Preparation:",
            "1. Review the petition or materials you'll be using",
            "2. Check weather conditions and dress appropriately",
            "3. Ensure all equipment is in good condition",
            "4. Confirm your assignment and route with management",
            "5. Test your phone battery and confirm connectivity",
        ]
    },
    "Station Setup Guide": {
        "subtitle": "Creating an Effective Engagement Station",
        "content": [
            "Whether you're setting up at a physical location or conducting door-to-door outreach, proper station setup is crucial for success. A well-organized station encourages participation and demonstrates professionalism.",
            
            "Physical Setup Best Practices:",
            "• Choose high-traffic areas with good visibility",
            "• Position yourself at eye level with passersby (avoid sitting in ways that seem unfriendly)",
            "• Keep materials organized and within easy reach",
            "• Maintain a clear, open posture that invites approach",
            "• Ensure adequate lighting if working in low-light conditions",
            
            "Materials Organization:",
            "• Petitions on top (most visible item)",
            "• Information sheets organized and easy to distribute",
            "• Pens accessible but not messy",
            "• Completed petitions in a separate folder",
            "• Business cards or contact information readily available",
            
            "Environmental Considerations:",
            "• Weather: Have protection from sun, rain, or wind",
            "• Foot traffic patterns: Position yourself where people naturally pause",
            "• Safety: Ensure clear sightlines and awareness of surroundings",
            "• Noise level: Be able to communicate clearly without shouting",
            
            "Remember: Your station setup communicates professionalism before you speak a word. Invest time in getting it right.",
        ]
    },
    "Objection Handling Guide": {
        "subtitle": "Responding to Common Concerns",
        "content": [
            "Objections are a natural part of the engagement process. They're not rejections—they're opportunities to provide more information and build trust. This guide provides strategies for handling common concerns professionally.",
            
            "Core Objection Handling Strategy:",
            "1. Listen fully without interrupting",
            "2. Acknowledge the concern with empathy",
            "3. Provide relevant information that addresses it",
            "4. Check understanding and invite continued dialogue",
            
            "Common Objections and Responses:",
            
            "Objection: 'I don't have time right now.'",
            "Response: 'I understand. This only takes 30 seconds if you're interested. I can also leave you information to read at your convenience.'",
            
            "Objection: 'I'm not interested.'",
            "Response: 'I appreciate your honesty. Could I ask why? Your feedback helps us improve our message.'",
            
            "Objection: 'Is this a scam?'",
            "Response: 'That's a fair question. [Provide credentials, show official materials, offer references.]'",
            
            "Objection: 'I don't agree with your cause.'",
            "Response: 'I respect your perspective. Would you be open to hearing our position? We value diverse viewpoints.'",
            
            "Golden Rules:",
            "• Never argue or become defensive",
            "• Listen more than you talk",
            "• Find common ground before presenting your message",
            "• Accept refusals gracefully—some people won't be interested",
        ]
    },
    "End of Day Wrap-Up": {
        "subtitle": "Closing Your Shift Professionally",
        "content": [
            "How you end your shift is just as important as how you begin it. Proper wrap-up ensures accurate reporting, protects materials, and sets the stage for the next team member or your next shift.",
            
            "Physical Asset Management:",
            "1. Count completed petitions carefully",
            "2. Return unused petitions in original quantity (or note shortfall)",
            "3. Collect all pens and materials",
            "4. Check the work area for any items left behind",
            "5. Secure materials in designated storage",
            
            "Reporting Your Results:",
            "• Document the number of completed petitions",
            "• Note the location and time worked",
            "• Record any unusual occurrences or feedback",
            "• Identify which petitions might have follow-up needs",
            "• Report any equipment issues or restocking needs",
            
            "Communication with Management:",
            "• Summarize your session's accomplishments",
            "• Report any challenges or learning points",
            "• Share positive feedback from supporters",
            "• Ask questions about anything unclear",
            
            "Personal Reflection:",
            "• What went well today?",
            "• What could be improved?",
            "• Did you follow the ethical guidelines?",
            "• How did you handle objections?",
            
            "Preparation for Next Session:",
            "• Review notes for areas to focus on next time",
            "• Identify patterns in supporter responses",
            "• Plan adjustments to your approach if needed",
        ]
    },
    "Data Mapping & Technology": {
        "subtitle": "Using Technology to Support Your Work",
        "content": [
            "Modern outreach relies on data management and technology tools. Understanding how to work with these systems is essential for tracking impact, improving efficiency, and supporting the broader mission.",
            
            "Data Entry Best Practices:",
            "• Accuracy is paramount—verify all information before submitting",
            "• Legible handwriting ensures data can be read correctly",
            "• Include all required fields—don't leave anything blank",
            "• Double-check contact information for accuracy",
            "• Note any special circumstances or follow-up needs",
            
            "Technology Tools You'll Use:",
            "• Mobile applications for real-time tracking",
            "• Database systems for petition information",
            "• Communication platforms for team coordination",
            "• Reporting dashboards for monitoring progress",
            
            "Data Security and Privacy:",
            "• Protect personal information of supporters and colleagues",
            "• Never share access credentials with unauthorized people",
            "• Follow all protocols for handling sensitive data",
            "• Report any security concerns immediately",
            "• Understand data retention and deletion policies",
            
            "Troubleshooting Technology Issues:",
            "• Document what went wrong and when",
            "• Take screenshots or photos of error messages",
            "• Contact tech support with specific details",
            "• Document workarounds you use in the meantime",
            "• Provide feedback about technology problems to improve systems",
        ]
    },
    "Mission Impact & Results": {
        "subtitle": "Understanding How Your Work Creates Change",
        "content": [
            "Every petition you collect, every conversation you have, and every person you engage contributes to broader impact. Understanding this connection keeps motivation high and work meaningful.",
            
            "The Impact Chain:",
            "Your Engagement → Petition Signature → Collective Voice → Organizational Action → Real-World Impact",
            
            "Measuring Success Beyond Numbers:",
            "• Connections made: How many meaningful conversations did you have?",
            "• Trust built: Did people feel respected and heard?",
            "• Understanding increased: Did people learn about the initiative?",
            "• Community strengthened: Did you contribute to a sense of shared purpose?",
            
            "Examples of Impact:",
            "• 100 petition signatures demonstrate community support to decision-makers",
            "• Your professionalism influenced 50 people's perception of the organization",
            "• Your ethical approach created 20 new advocates for the cause",
            "• Your enthusiasm inspired 10 people to get involved further",
            
            "Organizational Goals We're Supporting:",
            "• Build a broad coalition of community support",
            "• Establish credibility and legitimacy",
            "• Create momentum for change",
            "• Develop long-term volunteer relationships",
            
            "Your Personal Growth:",
            "• Develop communication and persuasion skills",
            "• Build confidence in professional interactions",
            "• Learn about our communities and their needs",
            "• Grow as a professional and community member",
        ]
    },
    "Who Can Sign": {
        "subtitle": "Eligibility and Authorization Guidelines",
        "content": [
            "Understanding who can legally and ethically sign the petition is crucial. This ensures the integrity of the process and the validity of the petition itself.",
            
            "General Eligibility Criteria:",
            "• Must be 18 years old or older (in most jurisdictions)",
            "• Must be a resident of the jurisdiction affected",
            "• Must be of sound mind (able to understand what they're signing)",
            "• Must not be an employee of [relevant organization, if applicable]",
            
            "Information Required from Signers:",
            "• Full legal name (as it appears on official documents)",
            "• Current residential address",
            "• Contact information (phone or email)",
            "• Date of signature",
            "• Signature or explicit consent",
            
            "People Who Cannot Sign:",
            "• Non-residents of the affected jurisdiction",
            "• Minors (under 18 years old)",
            "• People with legally appointed guardians who handle legal matters",
            "• Anyone who has explicitly requested not to be contacted",
            
            "How to Verify Eligibility:",
            "• Ask basic qualifying questions conversationally",
            "• Verify they understand what they're signing",
            "• Ensure they're providing accurate information",
            "• When in doubt, ask for clarification",
            
            "Documentation:",
            "• Keep signers' information secure and private",
            "• Maintain records for audit purposes",
            "• Follow data protection regulations",
            "• Be prepared to explain eligibility requirements if challenged",
        ]
    },
    "Golden Rules & Professionalism": {
        "subtitle": "Core Principles for Success",
        "content": [
            "These fundamental principles apply to every interaction. They define what it means to be a professional representative of our organization.",
            
            "The Golden Rules:",
            "1. Treat everyone with respect, regardless of their response",
            "2. Be honest in all communications—never exaggerate or mislead",
            "3. Listen more than you talk—understand before persuading",
            "4. Follow up on commitments—say what you'll do, then do it",
            "5. Represent the organization with integrity—your actions reflect on all of us",
            "6. Take care of materials and equipment—treat them like they're valuable (they are)",
            "7. Support your teammates—lift others up, don't tear them down",
            "8. Stay professional at all times—manage emotions and frustration",
            
            "What Professionalism Looks Like:",
            "• Punctuality: Arrive on time, fully prepared",
            "• Appearance: Dress appropriately for the environment",
            "• Language: Speak clearly, avoid slang or inappropriate language",
            "• Attitude: Maintain positive energy and enthusiasm",
            "• Reliability: Follow through on responsibilities",
            "• Communication: Keep supervisors informed of issues",
            "• Problem-solving: Address issues constructively",
            
            "When You Make a Mistake:",
            "1. Acknowledge it immediately—don't hide or minimize",
            "2. Take responsibility—avoid blame-shifting",
            "3. Apologize sincerely if someone was affected",
            "4. Propose a solution—show how you'll fix it",
            "5. Follow through—make sure the fix actually works",
            
            "Remember: Professionalism is a choice you make every day. It's not always easy, but it's always worth it.",
        ]
    },
    "Avoiding Invalid Signatures": {
        "subtitle": "Maintaining Petition Integrity",
        "content": [
            "The validity and credibility of our petition depends on having legitimate signatures. Understanding what makes a signature invalid helps us maintain integrity and prevent problems later.",
            
            "Common Reasons Signatures Become Invalid:",
            "• Person was not eligible at the time (moved, underage, etc.)",
            "• Information is illegible or incomplete",
            "• Person did not understand what they were signing",
            "• Signature does not match stated identity",
            "• Person explicitly withdraws consent later",
            "• Duplicate signature from same person",
            
            "How to Prevent Invalid Signatures:",
            "• Clearly explain what the petition is for",
            "• Verify eligibility before asking for signature",
            "• Request legible name and accurate address",
            "• Make eye contact and confirm understanding",
            "• Don't pressure people—only collect willing signatures",
            "• Keep organized records to prevent duplicates",
            
            "Red Flags to Watch For:",
            "• Signatures that don't match the name",
            "• Addresses that seem incomplete or incorrect",
            "• Signers who seem confused about what they're signing",
            "• Names that are illegible or misspelled",
            "• The same person signing multiple times",
            "• Signatures that look forged or obviously not genuine",
            
            "What to Do If You Suspect a Problem:",
            "• Set aside the questionable petition",
            "• Document what made you suspicious",
            "• Report it to your supervisor immediately",
            "• Never attempt to alter or correct signatures yourself",
            "• Follow your organization's protocol for handling disputes",
            
            "Remember: Quality over quantity. Ten valid, genuine signatures are worth more than fifty questionable ones.",
        ]
    },
    "Safety & Professionalism": {
        "subtitle": "Protecting Yourself and Others",
        "content": [
            "Working in the field requires awareness of safety issues. These guidelines help you protect yourself, your colleagues, and the supporters you interact with.",
            
            "Personal Safety Practices:",
            "• Trust your instincts—if a situation feels unsafe, remove yourself",
            "• Stay aware of your surroundings—don't get absorbed in your phone",
            "• Keep valuable items secure—don't leave belongings unattended",
            "• Travel in pairs when possible, especially in unfamiliar areas",
            "• Maintain communication with supervisors about your location",
            "• Avoid working alone during nighttime or low-light hours",
            
            "Dealing with Difficult Situations:",
            "• Aggressive behavior: Move away from the person and alert supervisors",
            "• Harassment: Document it and report immediately",
            "• Threats: Take them seriously, remove yourself, and involve management",
            "• Trespassing concerns: Respect private property and move if asked",
            
            "Professional Boundaries:",
            "• Maintain appropriate physical distance—at least 2 feet",
            "• Don't touch people unless they initiate contact (handshake)",
            "• Keep conversations focused on the petition/initiative",
            "• Avoid sharing personal information beyond what's professional",
            "• Don't accept gifts or offers beyond a simple thank you",
            
            "Weather and Environmental Safety:",
            "• Dress appropriately for conditions—avoid heat/cold exhaustion",
            "• Stay hydrated throughout your shift",
            "• Take breaks when you need them—don't push through exhaustion",
            "• Be aware of traffic if working on roadways",
            "• Watch for uneven surfaces or hazards where you're standing",
            
            "When in Doubt, Pause and Ask:",
            "Your safety is paramount. If anything feels unsafe, report it and seek guidance.",
        ]
    },
    "The Fifteen Second Hook": {
        "subtitle": "Making Your First Impression Count",
        "content": [
            "You typically have only 15-30 seconds to capture someone's attention. This critical window determines whether they'll listen further or keep walking. Here's how to make it count.",
            
            "Structure of an Effective Hook:",
            "1. Attention Grab (3 seconds): Something that makes them pause",
            "2. Problem Statement (5 seconds): Why this matters",
            "3. Call to Action (5 seconds): What you're asking them to do",
            "4. Benefit (2 seconds): Why it's worth their time",
            
            "Examples of Effective Hooks:",
            
            "Hook #1: 'Hi! Do you care about [community issue]?'",
            "Problem: 'Right now, [specific problem is happening]'",
            "Action: 'We're collecting signatures to address it'",
            "Benefit: 'Your voice could help create real change'",
            
            "Hook #2: 'Can I show you something that takes 30 seconds?'",
            "Problem: 'This affects [relevant group]'",
            "Action: 'We're asking for support'",
            "Benefit: 'Together we can make a difference'",
            
            "Hook #3: 'Are you a [community/local resident]?'",
            "Problem: '[Problem that affects that community]'",
            "Action: 'Will you sign this petition?'",
            "Benefit: 'It only takes one minute'",
            
            "Delivery Tips:",
            "• Make eye contact and smile",
            "• Speak clearly at normal volume",
            "• Use natural, conversational language",
            "• Show genuine interest in their response",
            "• Be prepared for rejection—most people will say no",
            "• Don't take it personally—it's not about you",
            
            "Practice Your Hook:",
            "• Say it out loud until it feels natural",
            "• Record yourself and listen for improvements",
            "• Adjust based on what resonates with people",
            "• Keep it authentic to your personality",
        ]
    },
    "Maximizing Conversion": {
        "subtitle": "Turning Interest into Signatures",
        "content": [
            "Getting someone's attention is the first step. Converting that attention into a signature requires skill, authenticity, and strategy. This module covers proven techniques for maximizing success rates.",
            
            "The Conversion Funnel:",
            "Awareness → Interest → Understanding → Agreement → Signature",
            
            "Techniques for Each Stage:",
            
            "Building Interest:",
            "• Show enthusiasm—your energy is contagious",
            "• Share a brief, compelling story or statistic",
            "• Ask engaging questions that prompt thought",
            "• Listen more than you pitch",
            
            "Creating Understanding:",
            "• Explain the issue clearly in simple language",
            "• Address their specific concerns first",
            "• Use examples that relate to their experience",
            "• Check understanding: 'Does that make sense?'",
            
            "Facilitating Agreement:",
            "• Find common ground first",
            "• Ask for their feedback on the issue",
            "• Help them see how they're part of the solution",
            "• Acknowledge their concerns respectfully",
            
            "Closing the Signature:",
            "• Use assumptive language: 'Your name will be on here...'",
            "• Make it easy: 'Here's a pen, just sign here'",
            "• Positive reinforcement: 'Thank you for caring'",
            "• Never pressure—if they're hesitant, respect that",
            
            "Recovery Techniques:",
            "If someone initially says no:",
            "1. Don't give up immediately",
            "2. Ask why—their objection might be easily addressed",
            "3. Provide more information if needed",
            "4. Offer a graceful way to reconsider",
            "5. If they still decline, thank them anyway",
            
            "Remember: Genuine people convert better than aggressive salespeople. Focus on authentic connection, not just numbers.",
        ]
    },
    "Quality Control & Verification": {
        "subtitle": "Ensuring Excellence in Every Interaction",
        "content": [
            "Quality control isn't just a management responsibility—it's something every team member contributes to. Maintaining high standards ensures our petitions are legitimate, our interactions are professional, and our mission is advanced.",
            
            "Personal Quality Standards:",
            "• Legibility: Ensure all signatures and information are clearly written",
            "• Completeness: Verify that all required fields are filled in",
            "• Accuracy: Double-check information before submission",
            "• Professionalism: Maintain high standards in every interaction",
            "• Ethics: Never cut corners or compromise integrity",
            
            "Self-Check Process:",
            "Before completing a petition:",
            "1. Is the person's name legible and spelled correctly?",
            "2. Is the address complete and accurate?",
            "3. Is the signature present and genuine-looking?",
            "4. Have I verified their eligibility?",
            "5. Does the petition meet professional standards?",
            
            "Common Quality Issues:",
            "• Illegible names → Can't verify identity later",
            "• Incomplete addresses → Can't verify residency",
            "• Missing information → Petition may be invalidated",
            "• Duplicates → Reduces credibility",
            "• Unclear signatures → Appears questionable",
            
            "Improving Quality Over Time:",
            "• Review feedback from supervisors",
            "• Learn from examples of strong and weak petitions",
            "• Practice your approach with experienced colleagues",
            "• Ask for help when you're unsure",
            "• Continuously refine your technique",
            
            "Peer Quality Support:",
            "• Help newer team members understand quality standards",
            "• Share techniques that work well for you",
            "• Give constructive feedback to peers",
            "• Celebrate high-quality work",
            
            "Remember: The quality of your work now determines the success of the entire initiative later.",
        ]
    },
    "Troubleshooting Common Issues": {
        "subtitle": "Problem-Solving in the Field",
        "content": [
            "Even with the best preparation, unexpected issues arise. This guide helps you handle common problems professionally and effectively.",
            
            "Technical Issues:",
            
            "Problem: 'I've run out of petitions'",
            "Solution: Contact supervisor for replacement, document how many were collected",
            
            "Problem: 'Someone's address is unclear'",
            "Solution: Ask them to write it more clearly, or ask for clarification",
            
            "Problem: 'The pen isn't working'",
            "Solution: Have backup pens—always carry at least two extras",
            
            "People-Related Issues:",
            
            "Problem: 'Someone is being verbally abusive'",
            "Solution: Disengage politely, move to another location, report to supervisor",
            
            "Problem: 'A supporter has complex questions I can't answer'",
            "Solution: Be honest: 'That's a great question. Let me get you someone who can answer it thoroughly'",
            
            "Problem: 'Someone wants to withdraw their signature later'",
            "Solution: Respect their wishes, document the withdrawal, report to supervisor",
            
            "Situational Issues:",
            
            "Problem: 'Weather is making it difficult to work'",
            "Solution: Seek shelter if needed, take breaks, focus on indoor/covered locations",
            
            "Problem: 'Low foot traffic in my assigned area'",
            "Solution: Inform supervisor, discuss moving to higher-traffic area",
            
            "Problem: 'I'm feeling overwhelmed or discouraged'",
            "Solution: Take a break, talk to a colleague or supervisor, remember why this work matters",
            
            "When to Escalate:",
            "• Safety concerns → Report immediately",
            "• Ethical questions → Ask before proceeding",
            "• Conflicts with supporters → Involve supervisor",
            "• Equipment problems → Request assistance",
            "• Any situation that's unclear → Ask rather than guess",
            
            "Remember: There's no shame in asking for help. Getting guidance is smarter than making mistakes.",
        ]
    },
}

def create_pdf(module_title, filename):
    """Create a PDF for a specific training module."""
    if module_title not in PDF_CONTENT:
        print(f"Warning: No content mapping for '{module_title}'. Skipping.")
        return False
    
    content_data = PDF_CONTENT[module_title]
    
    # Create document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=16
    )
    
    # Build document
    story = []
    
    # Title
    story.append(Paragraph(module_title, title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Subtitle
    story.append(Paragraph(content_data['subtitle'], subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Content
    for item in content_data['content']:
        if item.startswith('•') or item.startswith('□') or item.startswith('1.') or item.startswith('2.') or item.startswith('3.') or item.startswith('4.'):
            # List items and numbered items
            story.append(Paragraph(item, body_style))
        else:
            # Regular paragraphs
            story.append(Paragraph(item, body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", footer_style))
    story.append(Paragraph("P2P Solutions - Training Module", footer_style))
    
    # Build PDF
    try:
        doc.build(story)
        return True
    except Exception as e:
        print(f"Error creating PDF for '{module_title}': {e}")
        return False

def main():
    """Generate all PDFs."""
    pdf_dir = "/home/soarer/freelance/ppl/ppl2ppl/static/sample_pdfs"
    
    # Create directory if it doesn't exist
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Mapping of filenames to module titles
    filename_to_title = {
        "mission_overview.pdf": "Mission Overview",
        "petition_document_overview.pdf": "Petition Document Overview",
        "ethical_engagement_guide.pdf": "Ethical Engagement Guide",
        "field_gear_checklist.pdf": "Field Gear Checklist",
        "station_setup_guide.pdf": "Station Setup Guide",
        "objection_handling_guide.pdf": "Objection Handling Guide",
        "end_of_day_wrapup.pdf": "End of Day Wrap-Up",
        "data_mapping_tech.pdf": "Data Mapping & Technology",
        "mission_impact.pdf": "Mission Impact & Results",
        "who_can_sign.pdf": "Who Can Sign",
        "golden_rules.pdf": "Golden Rules & Professionalism",
        "avoiding_invalid.pdf": "Avoiding Invalid Signatures",
        "safety_professionalism.pdf": "Safety & Professionalism",
        "fifteen_second_hook.pdf": "The Fifteen Second Hook",
        "maximizing_conversion.pdf": "Maximizing Conversion",
        "quality_check.pdf": "Quality Control & Verification",
        "troubleshooting.pdf": "Troubleshooting Common Issues",
    }
    
    print("Generating training module PDFs...")
    success_count = 0
    
    for filename, title in filename_to_title.items():
        filepath = os.path.join(pdf_dir, filename)
        print(f"Creating {filename}...", end=" ")
        
        if create_pdf(title, filepath):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print(f"\nComplete! Generated {success_count}/{len(filename_to_title)} PDFs")

if __name__ == "__main__":
    main()
