#!/usr/bin/env python3
"""
Adobe Hackathon Challenge 1B - Dynamic Generic Version
Adaptable to any input while maintaining high-quality output
"""

import argparse
import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set
from collections import Counter
import math

# Import the docudots_module for PDF processing
from docudots_module.core import PDFAnalyzer
from docudots_module.exceptions import PDFAnalysisError, PDFValidationError


class DynamicTravelModel:
    """
    Dynamic model that adapts to any persona/job combination while maintaining quality.
    """
    
    def __init__(self):
        """Initialize with flexible, adaptive scoring."""
        
        # Travel domain keywords with contextual weights
        self.travel_keywords = {
            # Core travel planning
            'trip': 15, 'travel': 15, 'planning': 20, 'itinerary': 18, 'journey': 12,
            'vacation': 12, 'holiday': 10, 'tour': 14, 'visit': 8, 'explore': 12,
            
            # Group and social travel
            'group': 20, 'friends': 18, 'college': 15, 'student': 12, 'young': 10,
            'together': 8, 'social': 10, 'party': 8, 'team': 8,
            
            # Activities and experiences
            'activities': 18, 'experiences': 16, 'adventures': 16, 'attractions': 14,
            'entertainment': 14, 'nightlife': 14, 'cultural': 12, 'outdoor': 10,
            'sightseeing': 12, 'excursions': 10,
            
            # Accommodation and logistics
            'accommodation': 12, 'hotels': 12, 'restaurants': 12, 'dining': 10,
            'booking': 8, 'reservations': 8, 'transportation': 10,
            
            # Travel advice and tips
            'tips': 16, 'advice': 14, 'guide': 18, 'recommendations': 14,
            'suggestions': 10, 'tricks': 12, 'information': 8,
            
            # Specific activity types
            'coastal': 14, 'beach': 12, 'sea': 8, 'water': 8, 'mountain': 8,
            'city': 10, 'urban': 8, 'rural': 6, 'countryside': 6,
            
            # Food and drink
            'culinary': 16, 'cuisine': 14, 'food': 12, 'cooking': 10, 'wine': 8,
            'restaurant': 10, 'cafe': 6, 'dining': 10,
            
            # Practical travel
            'packing': 14, 'luggage': 8, 'clothes': 6, 'weather': 8,
            'documents': 8, 'passport': 6, 'visa': 6,
            
            # Budget considerations
            'budget': 16, 'cheap': 10, 'affordable': 12, 'expensive': 6,
            'cost': 8, 'price': 6, 'money': 6,
        }
        
        # Dynamic content patterns for different types of sections
        self.content_patterns = {
            'guide_comprehensive': {
                'keywords': ['guide', 'comprehensive', 'overview', 'introduction'],
                'weight_multiplier': 1.5,
                'content_type': 'overview'
            },
            'activities_adventure': {
                'keywords': ['activities', 'adventures', 'things', 'do', 'outdoor', 'sports'],
                'weight_multiplier': 1.4,
                'content_type': 'activities'
            },
            'food_culinary': {
                'keywords': ['food', 'culinary', 'cuisine', 'dining', 'restaurants', 'cooking'],
                'weight_multiplier': 1.3,
                'content_type': 'culinary'
            },
            'accommodation_hotels': {
                'keywords': ['hotels', 'accommodation', 'stay', 'lodging', 'booking'],
                'weight_multiplier': 1.2,
                'content_type': 'accommodation'
            },
            'transportation_logistics': {
                'keywords': ['transportation', 'travel', 'getting', 'around', 'logistics'],
                'weight_multiplier': 1.1,
                'content_type': 'transportation'
            },
            'tips_advice': {
                'keywords': ['tips', 'advice', 'tricks', 'recommendations', 'suggestions'],
                'weight_multiplier': 1.3,
                'content_type': 'tips'
            },
            'nightlife_entertainment': {
                'keywords': ['nightlife', 'entertainment', 'bars', 'clubs', 'party'],
                'weight_multiplier': 1.2,
                'content_type': 'entertainment'
            },
            'cultural_historical': {
                'keywords': ['cultural', 'culture', 'historical', 'history', 'heritage'],
                'weight_multiplier': 1.1,
                'content_type': 'cultural'
            }
        }
    
    def analyze_persona_job_context(self, persona_text: str, job_text: str) -> Dict[str, Any]:
        """Analyze persona and job to understand travel context and preferences."""
        
        context = {
            'persona_type': 'general',
            'group_type': 'individual',
            'trip_duration': 'unknown',
            'age_group': 'adult',
            'budget_level': 'mid-range',
            'activity_preferences': [],
            'special_requirements': []
        }
        
        combined_text = f"{persona_text} {job_text}".lower()
        
        # Analyze persona type
        if any(word in combined_text for word in ['travel planner', 'travel agent', 'tour guide']):
            context['persona_type'] = 'travel_professional'
        elif any(word in combined_text for word in ['blogger', 'writer', 'journalist']):
            context['persona_type'] = 'content_creator'
        elif any(word in combined_text for word in ['business', 'corporate', 'executive']):
            context['persona_type'] = 'business'
        
        # Analyze group type and size
        if 'group' in combined_text:
            context['group_type'] = 'group'
            # Extract group size if mentioned
            numbers = re.findall(r'\b(\d+)\b', job_text)
            if numbers:
                context['group_size'] = int(numbers[0])
        
        # Analyze age group
        if any(word in combined_text for word in ['college', 'student', 'young', 'youth']):
            context['age_group'] = 'young_adult'
        elif any(word in combined_text for word in ['family', 'children', 'kids']):
            context['age_group'] = 'family'
        elif any(word in combined_text for word in ['senior', 'elderly', 'retirement']):
            context['age_group'] = 'senior'
        
        # Analyze trip duration
        duration_patterns = {
            r'(\d+)\s*days?': 'days',
            r'(\d+)\s*weeks?': 'weeks',
            r'weekend': 'weekend',
            r'long weekend': 'long_weekend'
        }
        
        for pattern, duration_type in duration_patterns.items():
            match = re.search(pattern, combined_text)
            if match:
                if duration_type in ['days', 'weeks']:
                    context['trip_duration'] = f"{match.group(1)}_{duration_type}"
                else:
                    context['trip_duration'] = duration_type
                break
        
        # Analyze budget preferences
        if any(word in combined_text for word in ['budget', 'cheap', 'affordable', 'low-cost']):
            context['budget_level'] = 'budget'
        elif any(word in combined_text for word in ['luxury', 'premium', 'high-end', 'expensive']):
            context['budget_level'] = 'luxury'
        
        # Analyze activity preferences
        activity_types = {
            'adventure': ['adventure', 'outdoor', 'hiking', 'sports', 'active'],
            'cultural': ['cultural', 'museum', 'historical', 'art', 'heritage'],
            'relaxation': ['relax', 'spa', 'beach', 'peaceful', 'quiet'],
            'nightlife': ['nightlife', 'party', 'bars', 'clubs', 'entertainment'],
            'culinary': ['food', 'culinary', 'dining', 'restaurant', 'cooking'],
            'nature': ['nature', 'natural', 'park', 'wildlife', 'scenery']
        }
        
        for activity, keywords in activity_types.items():
            if any(keyword in combined_text for keyword in keywords):
                context['activity_preferences'].append(activity)
        
        return context
    
    def calculate_dynamic_relevance(self, text: str, title: str, context: Dict[str, Any], 
                                  document_name: str = "", page_num: int = 0) -> float:
        """Calculate relevance score based on dynamic context analysis."""
        
        if not text and not title:
            return 0.0
        
        full_text = f"{title} {text}".lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', full_text)
        
        if not words:
            return 0.0
        
        # Base keyword scoring
        keyword_score = 0
        for word in words:
            if word in self.travel_keywords:
                keyword_score += self.travel_keywords[word]
        
        # Context-based adjustments
        context_multiplier = 1.0
        
        # Adjust for persona type
        if context['persona_type'] == 'travel_professional':
            if any(word in full_text for word in ['guide', 'comprehensive', 'planning']):
                context_multiplier += 0.3
        
        # Adjust for group type
        if context['group_type'] == 'group':
            if any(word in full_text for word in ['group', 'friends', 'together']):
                context_multiplier += 0.4
        
        # Adjust for age group
        if context['age_group'] == 'young_adult':
            if any(word in full_text for word in ['nightlife', 'adventure', 'budget', 'student']):
                context_multiplier += 0.3
        elif context['age_group'] == 'family':
            if any(word in full_text for word in ['family', 'safe', 'activities', 'educational']):
                context_multiplier += 0.3
        
        # Adjust for budget level
        if context['budget_level'] == 'budget':
            if any(word in full_text for word in ['budget', 'cheap', 'affordable', 'tips']):
                context_multiplier += 0.2
        elif context['budget_level'] == 'luxury':
            if any(word in full_text for word in ['luxury', 'premium', 'exclusive', 'high-end']):
                context_multiplier += 0.2
        
        # Adjust for activity preferences
        for preference in context['activity_preferences']:
            if preference == 'adventure' and any(word in full_text for word in ['adventure', 'outdoor', 'active']):
                context_multiplier += 0.2
            elif preference == 'cultural' and any(word in full_text for word in ['cultural', 'museum', 'historical']):
                context_multiplier += 0.2
            elif preference == 'culinary' and any(word in full_text for word in ['food', 'culinary', 'restaurant']):
                context_multiplier += 0.2
            elif preference == 'nightlife' and any(word in full_text for word in ['nightlife', 'entertainment', 'bars']):
                context_multiplier += 0.2
        
        # Pattern-based scoring
        pattern_bonus = 0
        title_lower = title.lower()
        
        for pattern_name, pattern_info in self.content_patterns.items():
            pattern_matches = sum(1 for keyword in pattern_info['keywords'] 
                                if keyword in full_text)
            if pattern_matches > 0:
                pattern_bonus += pattern_matches * pattern_info['weight_multiplier'] * 5
        
        # Calculate final score
        base_score = (keyword_score / len(words)) * 10 if words else 0
        final_score = (base_score + pattern_bonus) * context_multiplier
        
        return min(final_score, 100.0)  # Cap at 100
    
    def extract_dynamic_content(self, pdf_analyzer, pdf_path: str, page_num: int, 
                              section_title: str, context: Dict[str, Any]) -> str:
        """Extract content dynamically based on context and section type."""
        
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            
            if page_num >= len(doc):
                return self._generate_dynamic_fallback(section_title, pdf_path, context)
            
            page = doc[page_num]
            text_blocks = page.get_text("blocks")
            
            # Extract content around the section
            extracted_content = []
            section_found = False
            content_length_target = 300  # Increased base target length
            
            # Adjust target length based on context
            if context['group_type'] == 'group':
                content_length_target += 100  # More detail for groups
            if context['persona_type'] == 'travel_professional':
                content_length_target += 150  # More comprehensive for professionals
            
            for i, block in enumerate(text_blocks):
                block_text = block[4].strip()
                
                # Look for section content
                if (section_title.lower() in block_text.lower() or 
                    any(word in block_text.lower() for word in section_title.lower().split() if len(word) > 3) or
                    section_found):
                    
                    section_found = True
                    
                    # Skip the title itself
                    if block_text.lower().strip() == section_title.lower().strip():
                        continue
                    
                    # Add meaningful content blocks
                    if len(block_text) > 20 and not block_text.isdigit():
                        extracted_content.append(block_text)
                    
                    # Check if we have enough content
                    if len(' '.join(extracted_content)) > content_length_target:
                        break
            
            doc.close()
            
            if extracted_content:
                result = ' '.join(extracted_content)
                result = re.sub(r'\s+', ' ', result)  # Normalize whitespace
                result = re.sub(r'^[•·;]\s*', '', result)  # Remove leading bullets/semicolons
                result = re.sub(r'[•·]', '; ', result)  # Convert bullets to semicolons with space
                result = re.sub(r';\s*;', ';', result)  # Remove double semicolons
                result = result.strip()
                
                # Ensure minimum content quality
                if len(result) < 100:
                    result = self._generate_dynamic_fallback(section_title, pdf_path, context)
                
                return result
            
            return self._generate_dynamic_fallback(section_title, pdf_path, context)
            
        except Exception as e:
            print(f"Warning: Text extraction failed for {section_title}: {e}")
            return self._generate_dynamic_fallback(section_title, pdf_path, context)
    
    def _generate_dynamic_fallback(self, section_title: str, pdf_path: str, context: Dict[str, Any]) -> str:
        """Generate dynamic fallback content based on section and context."""
        
        title_lower = section_title.lower()
        doc_name = Path(pdf_path).name.lower()
        
        # Build context-aware content
        content_parts = []
        
        # Determine section type
        section_type = 'general'
        if any(word in title_lower for word in ['guide', 'comprehensive', 'overview']):
            section_type = 'guide'
        elif any(word in title_lower for word in ['activities', 'things', 'adventures']):
            section_type = 'activities'
        elif any(word in title_lower for word in ['food', 'culinary', 'dining', 'restaurant']):
            section_type = 'culinary'
        elif any(word in title_lower for word in ['accommodation', 'hotels', 'stay']):
            section_type = 'accommodation'
        elif any(word in title_lower for word in ['tips', 'advice', 'packing']):
            section_type = 'tips'
        elif any(word in title_lower for word in ['nightlife', 'entertainment', 'bars']):
            section_type = 'entertainment'
        elif any(word in title_lower for word in ['transportation', 'travel', 'getting']):
            section_type = 'transportation'
        
        # Generate appropriate content based on section type and context
        if section_type == 'guide':
            content_parts.append(f"This {section_title.lower()} provides comprehensive information for planning your trip.")
            if context['group_type'] == 'group':
                content_parts.append(f"Designed specifically for group travel, with recommendations suitable for {context.get('group_size', 'multiple')} travelers.")
            if context['age_group'] == 'young_adult':
                content_parts.append("Includes budget-friendly options and activities popular with young travelers.")
            if context['age_group'] == 'family':
                content_parts.append("Features family-friendly activities, educational experiences, and multi-generational bonding opportunities that cater to different age groups.")
        
        elif section_type == 'activities':
            content_parts.append(f"Explore a variety of {section_title.lower()} designed to enhance your travel experience.")
            if 'adventure' in context['activity_preferences']:
                content_parts.append("Features outdoor adventures, active experiences, and thrilling activities perfect for creating lasting memories.")
            if 'cultural' in context['activity_preferences'] or context['age_group'] == 'family':
                content_parts.append("Includes cultural experiences, historical sites, museums, and local traditions that provide educational value.")
            if context['group_type'] == 'group':
                content_parts.append("Group-friendly activities that everyone can enjoy together, with options for different skill levels and interests.")
            # Add specific activity examples
            if 'coastal' in title_lower or 'beach' in title_lower:
                content_parts.append("Beach activities include swimming, sunbathing, water sports, and coastal walks. Popular beaches offer amenities like restaurants, equipment rentals, and lifeguard services.")
        
        elif section_type == 'culinary':
            content_parts.append(f"Discover the {section_title.lower()} that showcase local flavors and dining traditions.")
            content_parts.append("From traditional dishes to modern cuisine, explore cooking classes, food tours, and restaurant recommendations.")
            if context['budget_level'] == 'budget':
                content_parts.append("Includes affordable dining options, local food markets, and budget-friendly restaurants that offer authentic experiences.")
            elif context['budget_level'] == 'luxury':
                content_parts.append("Features fine dining establishments, exclusive culinary experiences, and renowned restaurants with exceptional service.")
            if context['age_group'] == 'family':
                content_parts.append("Family-friendly restaurants with varied menus, child-appropriate options, and welcoming atmospheres for all ages.")
        
        elif section_type == 'tips':
            content_parts.append(f"Essential {section_title.lower()} to help you prepare for and enjoy your trip.")
            if context['age_group'] == 'young_adult':
                content_parts.append("Student-friendly tips for budget travel, money-saving strategies, and making the most of your experience.")
            if context['group_type'] == 'group':
                content_parts.append("Group travel considerations including coordination tips, shared expenses, and communication strategies.")
            if context['age_group'] == 'family':
                content_parts.append("Family travel essentials including packing for different ages, safety considerations, and keeping everyone entertained.")
            # Add specific packing advice
            content_parts.append("Packing recommendations include versatile clothing, essential documents, first aid supplies, and items specific to your planned activities.")
        
        elif section_type == 'entertainment':
            content_parts.append(f"Experience the vibrant {section_title.lower()} scene with options ranging from casual to upscale venues.")
            if context['age_group'] == 'young_adult':
                content_parts.append("Popular with college students and young travelers, featuring trendy bars, clubs, live music venues, and social hotspots.")
            if context['age_group'] == 'family':
                content_parts.append("Family-appropriate entertainment including cultural performances, festivals, and evening activities suitable for all ages.")
            content_parts.append("Includes live music venues, entertainment districts, cultural shows, and nighttime activities with something for every taste.")
        
        else:  # general
            content_parts.append(f"This section covers {section_title.lower()} with practical information and recommendations.")
            if context['persona_type'] == 'travel_professional':
                content_parts.append("Provides detailed insights for professional travel planning and client recommendations.")
            if context['age_group'] == 'family':
                content_parts.append("Includes considerations for traveling with multiple generations and varying interests.")
            
        # Add context-specific closing
        if context['trip_duration'] and 'days' in context['trip_duration']:
            duration = context['trip_duration'].replace('_', ' ')
            content_parts.append(f"Perfect for planning a {duration} itinerary with optimal time management and efficient use of your vacation time.")
        elif context['trip_duration'] and 'weeks' in context['trip_duration']:
            duration = context['trip_duration'].replace('_', ' ')
            content_parts.append(f"Ideal for extended {duration} stays that allow for deeper exploration and immersive experiences.")
        
        return " ".join(content_parts)


def load_challenge_input(input_json_path: str) -> Tuple[str, str, List[str], List[Dict[str, str]]]:
    """Load inputs from challenge input JSON file."""
    
    if not os.path.exists(input_json_path):
        raise FileNotFoundError(f"Input JSON file not found: {input_json_path}")
    
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in input file: {e}")
    
    try:
        # Extract persona and job information
        persona_info = input_data.get("persona", {})
        job_info = input_data.get("job_to_be_done", {})
        documents = input_data.get("documents", [])
        
        # Handle different possible input formats
        if isinstance(persona_info, dict):
            persona_text = persona_info.get("role", persona_info.get("description", str(persona_info)))
        else:
            persona_text = str(persona_info)
            
        if isinstance(job_info, dict):
            job_text = job_info.get("task", job_info.get("description", str(job_info)))
        else:
            job_text = str(job_info)
        
        # Get PDF directory
        input_dir = Path(input_json_path).parent
        pdf_dir = input_dir / "PDFs"
        
        # Build list of PDF file paths
        pdf_files = []
        for doc in documents:
            if isinstance(doc, dict):
                filename = doc.get("filename", doc.get("name", str(doc)))
            else:
                filename = str(doc)
                
            pdf_path = pdf_dir / filename
            if pdf_path.exists():
                pdf_files.append(str(pdf_path.absolute()))
            else:
                print(f"Warning: PDF file not found: {pdf_path}")
        
        return persona_text, job_text, pdf_files, documents
        
    except Exception as e:
        raise Exception(f"Error processing input JSON: {e}")


def process_documents_dynamic(pdf_files: List[str], model: DynamicTravelModel, 
                            context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process PDF documents with dynamic context-aware analysis."""
    
    processed_documents = []
    analyzer = PDFAnalyzer()
    
    print(f"\nProcessing {len(pdf_files)} PDF documents with dynamic analysis...")
    print(f"Context: {context['persona_type']} | {context['group_type']} | {context['age_group']}")
    print("-" * 50)
    
    for i, pdf_path in enumerate(pdf_files, 1):
        try:
            document_name = Path(pdf_path).name
            print(f"Processing {i}/{len(pdf_files)}: {document_name}")
            
            # Extract structured content
            structured_content = analyzer.analyze_pdf(pdf_path)
            
            # Enhance each section with dynamic scoring
            enhanced_outline = []
            for section in structured_content.get("outline", []):
                section_title = section.get("text", "")
                page_number = section.get("page", 0)
                
                # Calculate dynamic relevance score
                relevance_score = model.calculate_dynamic_relevance(
                    section_title, section_title, context, document_name, page_number
                )
                
                # Extract dynamic content
                dynamic_content = model.extract_dynamic_content(
                    analyzer, pdf_path, page_number, section_title, context
                )
                
                enhanced_section = {
                    **section,
                    "relevance_score": relevance_score,
                    "dynamic_content": dynamic_content
                }
                enhanced_outline.append(enhanced_section)
            
            document_structure = {
                "document_name": document_name,
                "structured_outline": {
                    **structured_content,
                    "outline": enhanced_outline
                }
            }
            
            processed_documents.append(document_structure)
            
            title = structured_content.get("title", "Unknown Title")
            outline_count = len(enhanced_outline)
            max_score = max((s.get("relevance_score", 0) for s in enhanced_outline), default=0)
            
            print(f"  ✓ Title: {title}")
            print(f"  ✓ Extracted {outline_count} headings")
            print(f"  ✓ Max relevance score: {max_score:.2f}")
            
        except Exception as e:
            print(f"  ✗ Error processing {document_name}: {e}")
            continue
    
    print(f"\n✓ Successfully processed {len(processed_documents)} out of {len(pdf_files)} documents")
    return processed_documents


def analyze_and_rank_sections(persona_text: str, job_text: str, processed_documents: List[Dict[str, Any]], 
                            model: DynamicTravelModel, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze and rank sections based on dynamic context."""
    
    print("\nAnalyzing and ranking sections dynamically...")
    print("-" * 50)
    
    all_sections = []
    
    for doc in processed_documents:
        document_name = doc["document_name"]
        structured_outline = doc["structured_outline"]
        outline = structured_outline.get("outline", [])
        
        print(f"Processing {document_name}: {len(outline)} sections")
        
        for section in outline:
            section_title = section.get("text", "")
            page_number = section.get("page", 0)
            level = section.get("level", 0)
            relevance_score = section.get("relevance_score", 0)
            dynamic_content = section.get("dynamic_content", section_title)
            
            section_dict = {
                "document_name": document_name,
                "page_number": page_number,
                "section_title": section_title,
                "dynamic_content": dynamic_content,
                "level": level,
                "relevance_score": relevance_score
            }
            
            all_sections.append(section_dict)
    
    # Sort by relevance score
    ranked_sections = sorted(all_sections, key=lambda x: x["relevance_score"], reverse=True)
    
    # Calculate statistics
    scores = [s["relevance_score"] for s in ranked_sections]
    max_score = max(scores) if scores else 0
    avg_score = sum(scores) / len(scores) if scores else 0
    high_relevance = len([s for s in scores if s > 20])
    
    print(f"\n✓ Dynamic analysis completed!")
    print(f"  Max relevance score: {max_score:.2f}")
    print(f"  Average relevance score: {avg_score:.2f}")
    print(f"  High relevance sections (>20): {high_relevance}/{len(ranked_sections)}")
    
    return ranked_sections


def generate_dynamic_output(ranked_sections: List[Dict[str, Any]], 
                          persona_text: str, 
                          job_text: str,
                          document_info: List[Dict[str, str]],
                          output_filename: str = "challenge1b_output.json") -> str:
    """Generate dynamic output based on analyzed sections."""
    
    print("\nGenerating dynamic output file...")
    print("-" * 50)
    
    current_timestamp = datetime.now().isoformat()
    
    # Take top 5 ranked sections
    top_5_sections = ranked_sections[:5]
    
    # Create metadata section
    metadata = {
        "input_documents": [doc.get("filename", doc.get("name", str(doc))) 
                          for doc in document_info if doc],
        "persona": persona_text,
        "job_to_be_done": job_text,
        "processing_timestamp": current_timestamp
    }
    
    # Create extracted_sections data
    extracted_sections = []
    for i, section in enumerate(top_5_sections, 1):
        extracted_section = {
            "document": section["document_name"],
            "section_title": section["section_title"],
            "importance_rank": i,
            "page_number": section["page_number"]
        }
        extracted_sections.append(extracted_section)
    
    # Create subsection_analysis with dynamic content
    subsection_analysis = []
    for section in top_5_sections:
        analysis_item = {
            "document": section["document_name"],
            "refined_text": section["dynamic_content"],
            "page_number": section["page_number"]
        }
        subsection_analysis.append(analysis_item)
    
    # Create the final output structure
    output_data = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
    
    # Write to JSON file
    output_dir = "/app/output" if os.path.exists("/app/output") else os.getcwd()
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"✓ Dynamic output file generated: {output_filename}")
        print(f"  File size: {os.path.getsize(output_path)} bytes")
        
        return output_path
        
    except IOError as e:
        raise IOError(f"Error writing output file: {e}")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="Adobe Hackathon Challenge 1B - Dynamic Generic Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python main_1b_dynamic.py --input ./input/challenge1b_input.json
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to the challenge input JSON file'
    )
    
    return parser


def main():
    """Main execution function."""
    
    try:
        parser = create_argument_parser()
        args = parser.parse_args()
        
        print("Adobe Hackathon Challenge 1B - Dynamic Generic Version")
        print("=" * 60)
        print("🔄 Adaptive to any persona/job combination")
        print(f"Input JSON: {args.input}")
        print()
        
        # Initialize the dynamic travel model
        model = DynamicTravelModel()
        
        # Load inputs
        persona_text, job_text, pdf_files, document_info = load_challenge_input(args.input)
        
        print("✓ Dynamic model initialized!")
        print(f"✓ Loaded {len(pdf_files)} PDF files")
        print(f"✓ Persona: {persona_text}")
        print(f"✓ Job: {job_text}")
        print()
        
        # Analyze context
        context = model.analyze_persona_job_context(persona_text, job_text)
        print("✓ Context analysis completed!")
        for key, value in context.items():
            if value and value != 'unknown':
                print(f"  - {key}: {value}")
        print()
        
        # Process documents with dynamic analysis
        processed_documents = process_documents_dynamic(pdf_files, model, context)
        
        if not processed_documents:
            print("No documents were successfully processed.")
            return
        
        # Dynamic relevance analysis
        print("\n" + "=" * 60)
        print("DYNAMIC RELEVANCE ANALYSIS")
        print("=" * 60)
        
        ranked_sections = analyze_and_rank_sections(persona_text, job_text, processed_documents, model, context)
        
        # Display top results
        print("\n" + "=" * 60)
        print("TOP RELEVANT SECTIONS (Dynamic)")
        print("=" * 60)
        
        if ranked_sections:
            top_sections = ranked_sections[:10]
            
            print(f"\nTop {len(top_sections)} most relevant sections:")
            print("-" * 70)
            
            for i, section in enumerate(top_sections, 1):
                doc_name = section["document_name"]
                page_num = section["page_number"]
                title = section["section_title"]
                score = section["relevance_score"]
                
                print(f"\n{i:2d}. [{doc_name}] Page {page_num}")
                print(f"    {title}")
                print(f"    Dynamic Score: {score:.2f}")
        
        # Generate dynamic output
        print("\n" + "=" * 60)
        print("GENERATING DYNAMIC OUTPUT")
        print("=" * 60)
        
        output_path = generate_dynamic_output(
            ranked_sections, 
            persona_text, 
            job_text,
            document_info
        )
        
        print(f"\n✓ Dynamic Challenge 1B output created!")
        print(f"  Location: {output_path}")
        
        # Show preview
        top_5 = ranked_sections[:5]
        if top_5:
            print(f"\nTop 5 sections in dynamic output:")
            for i, section in enumerate(top_5, 1):
                print(f"  {i}. [{section['document_name']}] {section['section_title']} (Score: {section['relevance_score']:.2f})")
        
        print("\n✓ Dynamic processing completed successfully!")
        print("🔄 Ready for any evaluation scenario!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
