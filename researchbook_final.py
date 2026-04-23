#!/usr/bin/env python3
"""
ResearchBook - Final Working Version 
Optimized queries to avoid memory issues
"""

from researchbook import ResearchBook
from enhanced_name_matching import EnhancedNameMatcher
from ai_keyword_extractor import AIKeywordExtractor
import json

class ResearchBookFinal(ResearchBook):
    
    def __init__(self):
        super().__init__()
        self.name_matcher = EnhancedNameMatcher()
        self.ai_extractor = AIKeywordExtractor()
    
    def lookup_person(self, name: str) -> dict:
        """
        ENHANCED Person Lookup with smart name matching
        Handles variations like "Per Olof" vs "Per-Olof", accents, case, etc.
        """
        print(f"🔍 Looking up: {name}")
        
        # Try original name first
        db1_profile = self._get_researcher_profile_db1_enhanced(name)
        db2_profile = self._get_thesis_activities_db2_enhanced(name)
        
        # If not found, try name variations
        if not db1_profile and not db2_profile:
            print(f" Trying name variations for: {name}")
            variations = self.name_matcher.generate_name_variations(name)
            
            for variation in variations[:5]:  # Try top 5 variations
                if variation == name:
                    continue  # Skip original (already tried)
                    
                print(f"   Trying: {variation}")
                db1_profile = self._get_researcher_profile_db1_enhanced(variation)
                db2_profile = self._get_thesis_activities_db2_enhanced(variation)
                
                if db1_profile or db2_profile:
                    print(f" Found match with variation: {variation}")
                    name = variation  # Use the variation that worked
                    break
        
        # Combine data
        combined_data = {
            "name": name,
            "found_in_db1": len(db1_profile) > 0,
            "found_in_db2": len(db2_profile) > 0, 
            "researcher_data": db1_profile,
            "thesis_data": db2_profile
        }
        
        # Generate AI summary if we found data
        if combined_data["found_in_db1"] or combined_data["found_in_db2"]:
            ai_prompt = self._create_person_analysis_prompt(combined_data)
            combined_data["ai_analysis"] = self.ai_query(ai_prompt)
        else:
            combined_data["ai_analysis"] = "Person not found in either database"
        
        return combined_data
    
    def _get_researcher_profile_db1_enhanced(self, name: str) -> list:
        """Enhanced DB1 search with fuzzy matching"""
        # First try exact match (original behavior)
        exact_results = self._get_researcher_profile_db1(name)
        if exact_results:
            return exact_results
        
        # If no exact match, try fuzzy search
        with self.db1_driver.session(database="neo4j") as session:
            # Get potential candidates with CONTAINS search
            query = """
            MATCH (p:Person)
            WHERE toLower(p.name) CONTAINS toLower($name_part)
               OR toLower($name_part) CONTAINS toLower(p.name)
            RETURN p.name as name, p.orcid_id as orcid_id,
                   p.orcid_keywords as orcid_keywords,
                   p.given_names as given_names,
                   p.family_name as family_name,
                   p.orcid_publication_count as total_publications
            LIMIT 20
            """
            
            # Try with first word of name
            name_words = name.split()
            search_term = name_words[0] if name_words else name
            
            result = session.run(query, name_part=search_term)
            candidates = [dict(record) for record in result]
            
            # Use fuzzy matching to find best matches
            matches = self.name_matcher.find_best_matches(name, candidates, 'name', threshold=0.6)
            
            if matches:
                print(f"   Fuzzy match found: {matches[0]['name']} (score: {matches[0]['_match_score']:.2f})")
                return [matches[0]]  # Return best match
        
        return []
    
    def _get_thesis_activities_db2_enhanced(self, name: str) -> list:
        """Enhanced DB2 search with fuzzy matching"""
        # First try exact match (original behavior)
        exact_results = self._get_thesis_activities_db2(name)
        if exact_results:
            return exact_results
        
        # If no exact match, try fuzzy search
        with self.db2_driver.session(database="neo4j") as session:
            # Get potential candidates
            query = """
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE toLower(p.name) CONTAINS toLower($name_part)
               OR toLower($name_part) CONTAINS toLower(p.name)
            WITH p, type(r) as role, count(t) as thesis_count,
                 collect(t.title)[..2] as sample_titles,
                 collect(t.keywords)[..5] as all_keywords_raw
            WITH p, role, thesis_count, sample_titles,
                 [keyword IN apoc.coll.flatten(all_keywords_raw) WHERE keyword IS NOT NULL] as keywords
            RETURN p.name as name, role, thesis_count, sample_titles, keywords
            LIMIT 20
            """
            
            # Try with first word of name  
            name_words = name.split()
            search_term = name_words[0] if name_words else name
            
            try:
                result = session.run(query, name_part=search_term)
                candidates = [dict(record) for record in result]
                
                # Use fuzzy matching to find best matches
                matches = self.name_matcher.find_best_matches(name, candidates, 'name', threshold=0.6)
                
                if matches:
                    print(f"   Fuzzy match found in DB2: {matches[0]['name']} (score: {matches[0]['_match_score']:.2f})")
                    return matches  # Return all matches (not just first)
            except Exception as e:
                print(f"   DB2 fuzzy search error: {e}")
                # Fall back to simpler query without apoc
                simple_query = """
                MATCH (p:Person)-[r]->(t:Thesis)
                WHERE toLower(p.name) CONTAINS toLower($name_part)
                WITH p, type(r) as role, count(t) as thesis_count,
                     collect(t.title)[..2] as sample_titles
                RETURN p.name as name, role, thesis_count, sample_titles
                LIMIT 10
                """
                
                result = session.run(simple_query, name_part=search_term)
                candidates = [dict(record) for record in result]
                matches = self.name_matcher.find_best_matches(name, candidates, 'name', threshold=0.6)
                
                if matches:
                    return matches
        
        return []
    
    def generate_field_brief(self, research_field: str) -> dict:
        """
        RESEARCHBOOK CORE FEATURE 3: Field Intelligence Brief (Optimized)
        """
        print(f" Generating field brief for: {research_field}")
        
        # Get researchers from DB2 (more reliable)
        db2_researchers = self._get_field_researchers_db2(research_field)
        
        # Get recent activity trends
        trends_data = self._get_field_trends(research_field)
        
        # Generate AI intelligence brief
        brief_prompt = f"""
        Generate a comprehensive research field intelligence brief for: "{research_field}"
        
        RESEARCHERS IN FIELD (from thesis database):
        {json.dumps(db2_researchers, indent=2)}
        
        RECENT ACTIVITY TRENDS:
        {json.dumps(trends_data, indent=2)}
        
        Please provide:
        1. **Field Overview**: Current state of "{research_field}" research
        2. **Key Players**: Top researchers and their expertise
        3. **Activity Patterns**: Supervision, examination, collaboration trends
        4. **Research Focus Areas**: Main topics and themes
        5. **Growth Trends**: Recent developments and momentum
        6. **Opportunities**: Collaboration potential and emerging areas
        
        Keep response comprehensive but under 1000 words.
        """
        
        try:
            ai_brief = self.ai_query(brief_prompt, max_tokens=1500)
        except Exception as e:
            ai_brief = f"AI analysis unavailable due to error: {str(e)}"
        
        return {
            "field": research_field,
            "researchers_found": len(db2_researchers),
            "db2_researchers_found": len(db2_researchers),
            "trends": trends_data,
            "ai_brief": ai_brief,  # Fixed key name
            "ai_intelligence_brief": ai_brief  # Keep both for compatibility
        }
    
    def _get_field_researchers_db2(self, field: str) -> list:
        """Get researchers in field from DB2 - optimized query"""
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE toLower(t.title) CONTAINS toLower($field) OR
                  any(keyword IN t.keywords WHERE toLower(keyword) CONTAINS toLower($field))
            WITH p, type(r) as role, count(t) as thesis_count,
                 collect(t.title)[..2] as sample_titles
            RETURN p.name as name,
                   collect(DISTINCT role) as thesis_roles,
                   thesis_count,
                   sample_titles
            ORDER BY thesis_count DESC
            LIMIT 15
            """
            
            result = session.run(query, field=field)
            return [dict(record) for record in result]
    
    def _get_field_trends(self, field: str) -> dict:
        """Get recent trends - optimized"""
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            MATCH (t:Thesis)
            WHERE toLower(t.title) CONTAINS toLower($field) OR
                  any(keyword IN t.keywords WHERE toLower(keyword) CONTAINS toLower($field))
            WITH t.created_date.year as year, count(t) as count
            WHERE year >= 2020 AND year IS NOT NULL
            RETURN year, count
            ORDER BY year DESC
            LIMIT 10
            """
            
            result = session.run(query, field=field)
            yearly_data = [dict(record) for record in result]
            
            return {
                "yearly_activity": yearly_data,
                "total_recent": sum(record["count"] for record in yearly_data)
            }
    
    def parse_user_intent(self, user_input: str) -> dict:
        """
        RESEARCHBOOK SMART FEATURE: Parse user intent with AI
        LLM-first approach with pattern matching fallback
        """
        # Try LLM first for intelligent parsing
        
        parser_prompt = f"""
        Analyze this user query and extract structured information:
        
        USER INPUT: "{user_input}"
        
        Please identify:
        1. **Query Type**: person_lookup, expert_finder, field_intelligence, researcher_matching, or meeting_recommendation
        2. **Key Entities**: Names, research topics, organizations mentioned
        3. **Filters**: Any organization, time period, or other constraints
        4. **Intent**: What exactly does the user want to accomplish?
        5. **Output Format**: How should results be presented?
        6. **Specific Requirements**: Numbers, exclusions, groupings, or special formatting
        
        **Meeting Recommendation Indicators**: "visiting", "who should attend", "who should meet", "meeting with", "is coming", "[person] from [organization]", "relations", "connections", "network", "collaboration", "should meet", "recommendations"
        
        Examples:
        "Find me AI experts at Chalmers" → Type: expert_finder, Topic: "artificial intelligence", Filter: "Chalmers"
        "Erik Bohlin relations" → Type: meeting_recommendation, Visitor: "Erik Bohlin", Format: "standard"
        "show me all types of hard relations for Erik Bohlin" → Type: meeting_recommendation, Visitor: "Erik Bohlin", Format: "grouped_by_type", Filter: "hard_only"
        "give me 2 hard, 2 mjuk som inte keyword_similarity to Erik Bohlin" → Type: meeting_recommendation, Visitor: "Erik Bohlin", Numbers: "2_hard_2_mjuk", Exclude: "keyword_similarity"
        "what kinds of connections does Erik have" → Type: meeting_recommendation, Visitor: "Erik", Format: "types_overview" 
        "break down by relation types for Tiina" → Type: meeting_recommendation, Visitor: "Tiina", Format: "grouped_by_type"
        "show medförfattare and handledarnätverk for Erik" → Type: meeting_recommendation, Visitor: "Erik", Include: "medforfattare,handledarnatverk"
        "all hard relation types for Erik" → Type: meeting_recommendation, Visitor: "Erik", Format: "types_breakdown", Filter: "hard_only"
        "Erik Bohlin network breakdown" → Type: meeting_recommendation, Visitor: "Erik Bohlin", Format: "detailed_breakdown"
        "Anders Andersson publications" → Type: person_lookup, Person: "Anders Andersson"
        "What's happening in sustainability research?" → Type: field_intelligence, Field: "sustainability"
        
        Respond in JSON format:
        {{
            "query_type": "...",
            "entities": {{
                "person_name": "...",
                "research_topic": "...",
                "visitor_name": "...",
                "home_organization": "...",
                "research_field": "..."
            }},
            "filters": {{
                "organization": "...",
                "hard_only": false,
                "mjuk_only": false,
                "include_types": [],
                "exclude_types": [],
                "numbers": ""
            }},
            "output_format": "standard",
            "confidence": 0.9,
            "clarification_needed": "..."
        }}
        """
        
        try:
            ai_response = self.ai_query(parser_prompt, max_tokens=400)
            import json
            import re
            
            # Extract JSON from LLM response more robustly
            clean_response = ai_response.strip()
            
            # Remove markdown code blocks
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            # Try to extract JSON object even if there's extra text
            json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                result = json.loads(json_text)
                print(f" LLM parsed query as: {result.get('query_type')} (confidence: {result.get('confidence')})")
                return result
            else:
                # Try parsing the whole response as JSON
                result = json.loads(clean_response)
                print(f" LLM parsed query as: {result.get('query_type')} (confidence: {result.get('confidence')})")
                return result
            
        except Exception as e:
            print(f" LLM parsing completely failed: {str(e)}")
            print(f"Raw LLM response: {ai_response[:500]}...")  # Truncate for readability
            
            # NO FALLBACK - If LLM fails, we fail
            return {
                "query_type": "error",
                "entities": {},
                "filters": {},
                "output_format": "standard", 
                "confidence": 0.0,
                "clarification_needed": f"LLM parsing failed: {str(e)}. Please rephrase your query."
            }
    
    def _extract_name_from_query(self, query: str) -> str:
        """Extract person name from query text using pattern matching"""
        import re
        
        # Look for pattern: "Name from Organization"
        pattern_with_org = r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+from\s+"
        match = re.search(pattern_with_org, query)
        if match:
            return match.group(1)
        
        # Look for pattern: "Name is visiting" (without organization)  
        pattern_visiting = r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+is\s+visiting"
        match = re.search(pattern_visiting, query)
        if match:
            return match.group(1)
            
        # Look for pattern at start: "Name" followed by visiting keywords
        if "visiting" in query.lower() or "who should" in query.lower():
            pattern_start = r"^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)"
            match = re.search(pattern_start, query)
            if match:
                return match.group(1)
        
        # Fallback to known names (for testing)
        query_lower = query.lower()
        name_patterns = {
            "helena holmström olsson": "Helena Holmström Olsson",
            "jan bosch": "Jan Bosch",
            "anders skoogh": "Anders Skoogh", 
            "erik eriksson": "Erik Eriksson",
            "greg morrison": "Greg Morrison",
            "stefan stenfelt": "Stefan Stenfelt",
            "martin fabian": "Martin Fabian"
        }
        
        for pattern, name in name_patterns.items():
            if pattern in query_lower:
                return name
                
        return "Unknown Visitor"

    def _parse_relation_limits(self, user_input: str) -> dict:
        """Parse specific numbers and exclusions requested for HARD and MJUK relations"""
        import re
        
        user_lower = user_input.lower()
        
        # Default limits and exclusions
        result = {
            "hard": 5, 
            "mjuk": 5,
            "exclude_hard": [],
            "exclude_mjuk": []
        }
        
        # Look for patterns like "2 hard", "3 mjuk", "give me 4 hard and 2 mjuk"
        hard_patterns = [
            r'(\d+)\s+hard',
            r'(\d+)\s+hård',  # Swedish
            r'give me (\d+) hard',
            r'show me (\d+) hard'
        ]
        
        mjuk_patterns = [
            r'(\d+)\s+mjuk',
            r'(\d+)\s+soft',
            r'give me (\d+) mjuk',
            r'show me (\d+) mjuk'
        ]
        
        # Find HARD limits
        for pattern in hard_patterns:
            match = re.search(pattern, user_lower)
            if match:
                result["hard"] = int(match.group(1))
                break
        
        # Find MJUK limits  
        for pattern in mjuk_patterns:
            match = re.search(pattern, user_lower)
            if match:
                result["mjuk"] = int(match.group(1))
                break
        
        # Parse exclusions - look for "som inte X", "without X", "not X", "except X"
        exclusion_patterns = [
            r'som inte (\w+)',  # Swedish
            r'without (\w+)',
            r'not (\w+)',
            r'except (\w+)',
            r'exclude (\w+)'
        ]
        
        for pattern in exclusion_patterns:
            matches = re.findall(pattern, user_lower)
            for match in matches:
                # Map common relation names to actual system names
                relation_mapping = {
                    'keyword_similarity': 'keyword_similarity', 
                    'co_author_bridge': 'co_author_bridge',
                    'medforfattare': 'medforfattare',
                    'handledarnatverk': 'handledarnatverk',
                    'samma_alma_mater': 'samma_alma_mater',
                    'arbetade_samma_org': 'arbetade_samma_org'
                }
                
                if match in relation_mapping:
                    # Determine if it's HARD or MJUK relation to exclude
                    hard_relations = ['medforfattare', 'handledarnatverk', 'samma_alma_mater', 'arbetade_samma_org']
                    mjuk_relations = ['keyword_similarity', 'co_author_bridge']
                    
                    if relation_mapping[match] in hard_relations:
                        result["exclude_hard"].append(relation_mapping[match])
                    elif relation_mapping[match] in mjuk_relations:
                        result["exclude_mjuk"].append(relation_mapping[match])
        
        return result

    def strategic_meeting_recommendations(self, visitor_name: str, home_organization: str = None, limit: int = 10, user_query: str = "", output_format: str = "standard") -> dict:
        """
        RESEARCHBOOK SMART FEATURE: Strategic Meeting Assistant
        Find best researchers using HARD relations first, then MJUK relations
        """
        # Auto-detect organization if not specified
        if not home_organization:
            home_organization = "Chalmers"
            
        # Parse specific limits and exclusions from user query AND LLM interpretation
        limits = self._parse_relation_limits(user_query)
        
        # Also get exclusions and numbers from LLM parsing if available
        if hasattr(self, '_last_intent') and self._last_intent:
            llm_filters = self._last_intent.get('filters', {})
            llm_excludes = llm_filters.get('exclude_types', [])
            llm_numbers = llm_filters.get('numbers', '')
            
            # Handle number parsing from LLM
            if llm_numbers and llm_numbers.isdigit():
                total_requested = int(llm_numbers)
                # Split total between HARD and MJUK (roughly equal)
                limits['hard'] = total_requested // 2 + (total_requested % 2)  # Give extra to HARD if odd
                limits['mjuk'] = total_requested // 2
                print(f" LLM requested {total_requested} total connections: {limits['hard']} HARD + {limits['mjuk']} MJUK")
            
            # Map LLM exclusion names to system names
            exclusion_mapping = {
                'Medförfattare': 'medforfattare',
                'medförfattare': 'medforfattare',
                'Handledarnätverk': 'handledarnatverk', 
                'handledarnätverk': 'handledarnatverk',
                'Samma Alma Mater': 'samma_alma_mater',
                'samma alma mater': 'samma_alma_mater',
                'Arbetade samma organisation': 'arbetade_samma_org',
                'arbetade samma organisation': 'arbetade_samma_org',
                'cross_topic_matching': 'cross_topic_matching',
                'keyword_similarity': 'keyword_similarity',
                'co_author_bridge': 'co_author_bridge'
            }
            
            for llm_exclude in llm_excludes:
                if llm_exclude in exclusion_mapping:
                    mapped_name = exclusion_mapping[llm_exclude]
                    # Determine if HARD or MJUK
                    hard_types = ['medforfattare', 'handledarnatverk', 'samma_alma_mater', 'arbetade_samma_org']
                    if mapped_name in hard_types and mapped_name not in limits['exclude_hard']:
                        limits['exclude_hard'].append(mapped_name)
                    elif mapped_name not in hard_types and mapped_name not in limits['exclude_mjuk']:
                        limits['exclude_mjuk'].append(mapped_name)
        
        print(f" Finding meeting recommendations: {visitor_name} meeting {home_organization} researchers")
        print(f" Requested limits: {limits['hard']} HARD + {limits['mjuk']} MJUK relations")
        if limits['exclude_hard'] or limits['exclude_mjuk']:
            print(f" Exclusions: HARD={limits['exclude_hard']}, MJUK={limits['exclude_mjuk']}")
        
        # Step 1: Verify visitor exists in our databases
        visitor_profile = self.lookup_person(visitor_name)
        if not visitor_profile['found_in_db1'] and not visitor_profile['found_in_db2']:
            return {"error": f"Could not find profile for {visitor_name}. Please check the name or try a different variation."}
        
        # Step 2: Find ALL HARD relations and apply exclusions
        hard_relations_all = self._find_hard_relations(visitor_name, home_organization)
        hard_relations_filtered = [r for r in hard_relations_all if r.get('relation_type') not in limits['exclude_hard']]
        
        # Step 3: Find ALL MJUK relations and apply exclusions
        mjuk_relations_all = self._find_mjuk_relations(visitor_name, home_organization, limit)
        mjuk_relations_filtered = [r for r in mjuk_relations_all if r.get('relation_type') not in limits['exclude_mjuk']]
        
        # Step 4: Smart allocation - take what's available and backfill
        hard_available = len(hard_relations_filtered)
        mjuk_available = len(mjuk_relations_filtered)
        total_requested = limits['hard'] + limits['mjuk']
        
        print(f" Available: {hard_available} HARD + {mjuk_available} MJUK = {hard_available + mjuk_available} total")
        print(f" Requested: {limits['hard']} HARD + {limits['mjuk']} MJUK = {total_requested} total")
        
        # If we don't have enough HARD, take extra from MJUK
        hard_to_take = min(limits['hard'], hard_available)
        remaining_needed = total_requested - hard_to_take
        mjuk_to_take = min(remaining_needed, mjuk_available)
        
        # If we still need more and have extra HARD available, take more HARD
        if hard_to_take + mjuk_to_take < total_requested and hard_available > hard_to_take:
            extra_hard_needed = total_requested - hard_to_take - mjuk_to_take
            extra_hard_available = hard_available - hard_to_take
            hard_to_take += min(extra_hard_needed, extra_hard_available)
        
        # Ensure diversity - try to get examples from each HARD relation type
        hard_relations = self._select_diverse_hard_relations(hard_relations_filtered, hard_to_take)
        mjuk_relations = self._select_diverse_mjuk_relations(mjuk_relations_filtered, mjuk_to_take)
        
        print(f" Actually taking: {len(hard_relations)} HARD + {len(mjuk_relations)} MJUK = {len(hard_relations) + len(mjuk_relations)} total")
        
        # Combine results - allow same person with different relation types
        seen_relations = set()  # Track name+relation_type combinations instead of just names
        all_candidates = []
        final_hard_relations = []
        final_mjuk_relations = []
        
        # Add hard relations first (they take priority)
        for candidate in hard_relations:
            relation_key = f"{candidate['name']}_{candidate.get('relation_type', 'unknown')}"
            if relation_key not in seen_relations:
                seen_relations.add(relation_key)
                all_candidates.append(candidate)
                final_hard_relations.append(candidate)
        
        # Add mjuk relations - allow same person if different relation type
        for candidate in mjuk_relations:
            # Special handling for co_author_bridge - include bridge person in key
            if candidate.get('relation_type') == 'co_author_bridge':
                relation_key = f"{candidate['name']}_co_author_bridge_via_{candidate.get('bridge_person', 'unknown')}"
            else:
                relation_key = f"{candidate['name']}_{candidate.get('relation_type', 'unknown')}"
            
            if relation_key not in seen_relations:
                seen_relations.add(relation_key)
                all_candidates.append(candidate)
                final_mjuk_relations.append(candidate)
        
        # CRITICAL FIX: If user requested specific total, backfill to reach it
        # Check if LLM parsed a specific number
        if hasattr(self, '_last_intent') and self._last_intent:
            llm_filters = self._last_intent.get('filters', {})
            llm_numbers = llm_filters.get('numbers', '')
            if llm_numbers and llm_numbers.isdigit():
                total_requested = int(llm_numbers)
            else:
                total_requested = limits['hard'] + limits['mjuk']
        else:
            total_requested = limits['hard'] + limits['mjuk']
        current_total = len(all_candidates)
        
        if current_total < total_requested:
            print(f" Only found {current_total} unique relations, requested {total_requested} - backfilling...")
            
            # Get more from available pools using new relation key system
            all_available = []
            for rel in hard_relations_filtered + mjuk_relations_filtered:
                if rel.get('relation_type') == 'co_author_bridge':
                    relation_key = f"{rel['name']}_co_author_bridge_via_{rel.get('bridge_person', 'unknown')}"
                else:
                    relation_key = f"{rel['name']}_{rel.get('relation_type', 'unknown')}"
                
                if relation_key not in seen_relations:
                    all_available.append(rel)
            
            # Add more until we reach the target
            for candidate in all_available:
                if len(all_candidates) >= total_requested:
                    break
                
                if candidate.get('relation_type') == 'co_author_bridge':
                    relation_key = f"{candidate['name']}_co_author_bridge_via_{candidate.get('bridge_person', 'unknown')}"
                else:
                    relation_key = f"{candidate['name']}_{candidate.get('relation_type', 'unknown')}"
                
                if relation_key not in seen_relations:
                    seen_relations.add(relation_key)
                    all_candidates.append(candidate)
                    if candidate.get('relation_strength') == 'HARD':
                        final_hard_relations.append(candidate)
                    else:
                        final_mjuk_relations.append(candidate)
        
        # Update relations to use final counts
        hard_relations = final_hard_relations
        mjuk_relations = final_mjuk_relations
        
        print(f" FINAL: Delivering {len(all_candidates)} total relations ({len(hard_relations)} HARD + {len(mjuk_relations)} MJUK)")
        
        # Step 4: Enhanced AI analysis (optimized for performance)
        # Truncate data to prevent timeouts
        hard_summary = []
        for rel in hard_relations:  # Use actual limited results
            hard_summary.append({
                'name': rel.get('name'),
                'relation_type': rel.get('relation_type'), 
                'relation_strength': rel.get('relation_strength')
            })
            
        mjuk_summary = []
        for rel in mjuk_relations:  # Use actual limited results  
            mjuk_summary.append({
                'name': rel.get('name'),
                'relation_type': rel.get('relation_type'),
                'relation_strength': rel.get('relation_strength')
            })
        
        ai_prompt = f"""
        Brief meeting analysis for {visitor_name}:
        
        HARD RELATIONS: {[rel['name'] + ' (' + rel['relation_type'] + ')' for rel in hard_summary]}
        MJUK RELATIONS: {[rel['name'] + ' (' + rel['relation_type'] + ')' for rel in mjuk_summary]}
        
        Provide 3 short bullet points:
        • Top 3 priority attendees
        • Why hard relations matter  
        • Why mjuk relations matter
        
        Maximum 150 words total.
        """
        
        try:
            ai_analysis = self.ai_query(ai_prompt, max_tokens=800)
        except Exception as e:
            ai_analysis = f"AI analysis unavailable due to timeout. Found {len(hard_relations)} hard relations and {len(mjuk_relations)} mjuk relations. Hard relations include direct collaborations, mjuk relations include research area alignments."
        
        # Handle different output formats
        if output_format == "grouped_by_type":
            return self._format_by_relation_type(visitor_name, home_organization, hard_relations, mjuk_relations, ai_analysis)
        elif output_format == "types_overview":
            return self._format_types_overview(visitor_name, home_organization, hard_relations, mjuk_relations)
        elif output_format == "detailed_breakdown":
            return self._format_detailed_breakdown(visitor_name, home_organization, hard_relations, mjuk_relations, ai_analysis)
        else:
            # Standard format
            return {
                "visitor": visitor_name,
                "home_organization": home_organization,
                "hard_relations_found": len(hard_relations),
                "mjuk_relations_found": len(mjuk_relations),
                "recommended_participants": all_candidates,
                "participants_found": len(all_candidates),
                "strategic_analysis": ai_analysis,
                "output_format": output_format
            }

    def _format_by_relation_type(self, visitor_name: str, home_organization: str, hard_relations: list, mjuk_relations: list, ai_analysis: str) -> dict:
        """Format results grouped by relation type"""
        # Group HARD relations by type
        hard_by_type = {}
        for rel in hard_relations:
            rel_type = rel.get('relation_type', 'unknown')
            if rel_type not in hard_by_type:
                hard_by_type[rel_type] = []
            hard_by_type[rel_type].append(rel)
        
        # Group MJUK relations by type  
        mjuk_by_type = {}
        for rel in mjuk_relations:
            rel_type = rel.get('relation_type', 'unknown')
            if rel_type not in mjuk_by_type:
                mjuk_by_type[rel_type] = []
            mjuk_by_type[rel_type].append(rel)
        
        return {
            "visitor": visitor_name,
            "home_organization": home_organization,
            "output_format": "grouped_by_type",
            "hard_relations_by_type": hard_by_type,
            "mjuk_relations_by_type": mjuk_by_type,
            "total_hard_types": len(hard_by_type),
            "total_mjuk_types": len(mjuk_by_type),
            "strategic_analysis": ai_analysis
        }
    
    def _format_types_overview(self, visitor_name: str, home_organization: str, hard_relations: list, mjuk_relations: list) -> dict:
        """Format as overview of available relation types"""
        hard_types = {}
        for rel in hard_relations:
            rel_type = rel.get('relation_type', 'unknown')
            hard_types[rel_type] = hard_types.get(rel_type, 0) + 1
        
        mjuk_types = {}
        for rel in mjuk_relations:
            rel_type = rel.get('relation_type', 'unknown')  
            mjuk_types[rel_type] = mjuk_types.get(rel_type, 0) + 1
        
        return {
            "visitor": visitor_name,
            "home_organization": home_organization,
            "output_format": "types_overview", 
            "hard_relation_types": hard_types,
            "mjuk_relation_types": mjuk_types,
            "summary": f"Found {len(hard_types)} HARD relation types and {len(mjuk_types)} MJUK relation types"
        }

    def _format_detailed_breakdown(self, visitor_name: str, home_organization: str, hard_relations: list, mjuk_relations: list, ai_analysis: str) -> dict:
        """Format as detailed breakdown with full information"""
        return {
            "visitor": visitor_name,
            "home_organization": home_organization,
            "output_format": "detailed_breakdown",
            "hard_relations_detail": hard_relations,
            "mjuk_relations_detail": mjuk_relations,
            "hard_count": len(hard_relations),
            "mjuk_count": len(mjuk_relations),
            "strategic_analysis": ai_analysis,
            "breakdown_complete": True
        }
    
    def _find_hard_relations(self, visitor_name: str, home_organization: str) -> list:
        """
        Find ONLY the 4 specific HARD relations:
        1. Medförfattare (co-authors)  
        2. Handledarnätverk (supervision/examination)
        3. Båda studerade vid samma plats (same alma mater)
        4. Arbetade på samma organisation (temporal colleagues)
        """
        print(f" Finding 4 specific HARD relations for {visitor_name}")
        
        hard_relations = []
        
        # 1. MEDFÖRFATTARE (Database 1)
        co_authors = self._find_co_authors(visitor_name, home_organization)
        for author in co_authors:
            author['relation_type'] = 'medforfattare'
            author['relation_strength'] = 'HARD'
        hard_relations.extend(co_authors)
        
        # 2. HANDLEDARNÄTVERK - HANDLEDNING OCH EXAMINATION (Database 2) 
        academic_network = self._find_academic_network(visitor_name, home_organization)
        for academic in academic_network:
            academic['relation_type'] = 'handledarnatverk'
            academic['relation_strength'] = 'HARD'
        hard_relations.extend(academic_network)
        
        # 3. BÅDA STUDERADE VID SAMMA PLATS
        alma_mater_connections = self._find_same_alma_mater(visitor_name, home_organization)
        for alma in alma_mater_connections:
            alma['relation_type'] = 'samma_alma_mater'
            alma['relation_strength'] = 'HARD'
        hard_relations.extend(alma_mater_connections)
        
        # 4. ARBETADE PÅ SAMMA ORGANISATION (overlapping time periods)
        temporal_colleagues = self._find_temporal_colleagues(visitor_name, home_organization)
        for colleague in temporal_colleagues:
            colleague['relation_type'] = 'arbetade_samma_org' 
            colleague['relation_strength'] = 'HARD'
        hard_relations.extend(temporal_colleagues)
        
        print(f" Found {len(hard_relations)} HARD relations (4 types only)")
        return hard_relations[:15]
    
    def _select_diverse_hard_relations(self, hard_relations: list, limit: int) -> list:
        """Select HARD relations ensuring diversity across all 4 types"""
        if not hard_relations or limit <= 0:
            return []
        
        # Group by relation type
        by_type = {}
        for rel in hard_relations:
            rel_type = rel.get('relation_type', 'unknown')
            if rel_type not in by_type:
                by_type[rel_type] = []
            by_type[rel_type].append(rel)
        
        # Ensure we show examples from each type (round-robin)
        selected = []
        type_order = ['medforfattare', 'handledarnatverk', 'samma_alma_mater', 'arbetade_samma_org']
        
        # First pass: take 1 from each type
        for rel_type in type_order:
            if rel_type in by_type and by_type[rel_type] and len(selected) < limit:
                selected.append(by_type[rel_type].pop(0))
        
        # Second pass: fill remaining slots with any available
        remaining_relations = []
        for rel_type, relations in by_type.items():
            remaining_relations.extend(relations)
        
        for rel in remaining_relations:
            if len(selected) >= limit:
                break
            selected.append(rel)
        
        print(f" Selected {len(selected)} HARD relations with type diversity")
        type_counts = {}
        for rel in selected:
            rel_type = rel.get('relation_type', 'unknown')
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        print(f" Types selected: {dict(type_counts)}")
        
        return selected
    
    def _select_diverse_mjuk_relations(self, mjuk_relations: list, limit: int) -> list:
        """Select MJUK relations ensuring diversity between keyword similarity and co-author bridges"""
        if not mjuk_relations or limit <= 0:
            return []
        
        # Group by relation type
        keyword_sim = [r for r in mjuk_relations if r.get('relation_type') == 'keyword_similarity']
        co_bridges = [r for r in mjuk_relations if 'bridge' in r.get('relation_type', '')]
        
        selected = []
        
        # Strategy: Ensure both types are represented if both exist
        if keyword_sim and co_bridges:
            # Alternate between types
            remaining = limit
            
            # Start with keyword similarity (usually has lower scores, take first)
            keyword_to_take = min(len(keyword_sim), max(1, remaining // 2))
            selected.extend(keyword_sim[:keyword_to_take])
            remaining -= keyword_to_take
            
            # Then co-author bridges (sorted by score, take highest)
            co_bridges_sorted = sorted(co_bridges, key=lambda x: x.get('total_bridge_score', 0), reverse=True)
            bridges_to_take = min(len(co_bridges_sorted), remaining)
            selected.extend(co_bridges_sorted[:bridges_to_take])
            
            print(f" MJUK diversity: {keyword_to_take} keyword + {bridges_to_take} bridges")
            
        elif keyword_sim:
            # Only keyword similarity available
            selected.extend(keyword_sim[:limit])
            print(f" MJUK selection: {len(selected)} keyword similarity only")
            
        elif co_bridges:
            # Only co-author bridges available  
            co_bridges_sorted = sorted(co_bridges, key=lambda x: x.get('total_bridge_score', 0), reverse=True)
            selected.extend(co_bridges_sorted[:limit])
            print(f" MJUK selection: {len(selected)} co-author bridges only")
        
        return selected
    
    def _find_co_authors(self, visitor_name: str, home_organization: str) -> list:
        """Find people who co-authored publications with visitor"""
        with self.db1_driver.session(database="neo4j") as session:
            query = """
            // Find visitor's publications
            MATCH (visitor:Person)-[:AUTHORED]->(pub:Publication)<-[:AUTHORED]-(coauthor:Person)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND NOT toLower(coauthor.name) CONTAINS toLower($visitor_name)
            
            // Check if co-author is from target organization  
            MATCH (coauthor)-[w:WORKED_AT]->(org:Organization)
            WHERE toLower(org.name) CONTAINS toLower($org_name)
            
            // Get collaboration details
            WITH coauthor, visitor, 
                 count(DISTINCT pub) as shared_publications,
                 collect(DISTINCT pub.name)[..3] as sample_publications,
                 collect(DISTINCT w.department)[..2] as departments,
                 collect(DISTINCT w.role)[..2] as roles
            
            RETURN coauthor.name as name,
                   coauthor.orcid_id as orcid_id,
                   shared_publications,
                   sample_publications,
                   departments,
                   roles,
                   'co_author' as relation_type
            ORDER BY shared_publications DESC
            LIMIT 5
            """
            
            result = session.run(query, 
                               visitor_name=visitor_name,
                               org_name=home_organization)
            return [dict(record) for record in result]

    def _find_academic_network(self, visitor_name: str, home_organization: str) -> list:
        """Find supervision/examination network connections"""
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            // Find visitor's thesis relationships
            MATCH (visitor:Person)-[r1]->(thesis:Thesis)<-[r2]-(colleague:Person)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND NOT toLower(colleague.name) CONTAINS toLower($visitor_name)
            
            // Group by colleague and relationship types
            WITH colleague,
                 collect(DISTINCT type(r1)) as visitor_roles,
                 collect(DISTINCT type(r2)) as colleague_roles,
                 collect(DISTINCT thesis.title)[..2] as shared_theses,
                 count(DISTINCT thesis) as shared_thesis_count
            
            RETURN colleague.name as name,
                   visitor_roles,
                   colleague_roles, 
                   shared_theses,
                   shared_thesis_count,
                   CASE 
                     WHEN any(role IN colleague_roles WHERE role IN ['SUPERVISOR', 'ACADEMIC_SUPERVISOR', 'INDUSTRY_SUPERVISOR'])
                       THEN 'supervision_network'
                     WHEN any(role IN colleague_roles WHERE role IN ['EXAMINER', 'OPPONENT', 'REVIEWER'])
                       THEN 'examination_network'
                     ELSE 'academic_collaboration'
                   END as relation_type
            ORDER BY shared_thesis_count DESC
            LIMIT 5
            """
            
            result = session.run(query, visitor_name=visitor_name)
            return [dict(record) for record in result]

    def _find_temporal_colleagues(self, visitor_name: str, home_organization: str) -> list:
        """Find people who worked at same org during overlapping time periods"""
        with self.db1_driver.session(database="neo4j") as session:
            query = """
            // Find visitor's work periods
            MATCH (visitor:Person)-[vw:WORKED_AT]->(org:Organization)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND toLower(org.name) CONTAINS toLower($org_name)
            
            // Find colleagues with overlapping periods
            MATCH (colleague:Person)-[cw:WORKED_AT]->(org)
            WHERE NOT toLower(colleague.name) CONTAINS toLower($visitor_name)
              AND (
                (vw.start_year <= cw.end_year AND vw.end_year >= cw.start_year) OR
                (vw.start_year IS NULL OR cw.start_year IS NULL) OR
                (vw.end_year IS NULL OR cw.end_year IS NULL)
              )
            
            WITH colleague, org,
                 collect(DISTINCT cw.department) as departments,
                 collect(DISTINCT cw.role) as roles,
                 count(*) as overlap_periods
            
            RETURN colleague.name as name,
                   colleague.orcid_id as orcid_id,
                   departments,
                   roles,
                   overlap_periods,
                   org.name as organization
            ORDER BY overlap_periods DESC
            LIMIT 5
            """
            
            result = session.run(query,
                               visitor_name=visitor_name, 
                               org_name=home_organization)
            return [dict(record) for record in result]
    
    def _find_mjuk_relations(self, visitor_name: str, home_organization: str, limit: int) -> list:
        """
        Find MJUK relations: keyword similarity, research area overlap 
        These complement HARD relations to give a complete picture
        """
        print(f" Finding MJUK relations for {visitor_name}")
        
        mjuk_relations = []
        
        # Get visitor's research profile for keyword matching
        visitor_profile = self.lookup_person(visitor_name)
        
        # COMPREHENSIVE KEYWORD EXTRACTION
        visitor_keywords = self._extract_comprehensive_keywords(visitor_profile)
        
        # Find researchers with similar keywords (should always have some keywords now)
        similarity_matches = []
        if visitor_keywords:
            print(f" Using {len(visitor_keywords)} AI-extracted keywords for matching")
            similarity_matches = self._find_keyword_similarity(visitor_name, home_organization, visitor_keywords, limit)
        else:
            print(" No keywords could be extracted (should be rare)")
            
        for match in similarity_matches:
            match['relation_type'] = 'keyword_similarity'
            match['relation_strength'] = 'MJUK'
        mjuk_relations.extend(similarity_matches)
        
        # Add co-author bridges (X-Y-Z connections)
        co_author_bridges = self._find_co_author_bridges(visitor_name, home_organization, limit//3)
        for bridge in co_author_bridges:
            bridge['relation_type'] = 'co_author_bridge'
            bridge['relation_strength'] = 'MJUK'
        mjuk_relations.extend(co_author_bridges)
        
        print(f" Found {len(mjuk_relations)} MJUK relations")
        return mjuk_relations
    
    def _extract_comprehensive_keywords(self, visitor_profile: dict) -> list:
        """
        COMPREHENSIVE keyword extraction using AI and all available data sources
        This ensures EVERYONE has keywords for similarity matching
        """
        all_keywords = []
        
        # Step 1: Get existing pre-tagged keywords (fast)
        print(" Step 1: Collecting existing keywords...")
        for researcher in visitor_profile.get('researcher_data', []):
            if researcher.get('orcid_keywords'):
                all_keywords.extend(researcher['orcid_keywords'])
                print(f"   Added {len(researcher['orcid_keywords'])} ORCID keywords")
        
        for thesis in visitor_profile.get('thesis_data', []):
            if thesis.get('keywords'):
                all_keywords.extend(thesis['keywords'])
                print(f"   Added {len(thesis['keywords'])} thesis keywords")
        
        # Step 2: AI extraction from publications (titles, abstracts)
        print(" Step 2: AI extraction from publications...")
        if visitor_profile.get('researcher_data'):
            for researcher in visitor_profile['researcher_data']:
                # Get this person's publications for AI analysis
                publications = self._get_person_publications(researcher.get('name', ''))
                if publications:
                    ai_keywords = self.ai_extractor.extract_keywords_from_publications(publications)
                    all_keywords.extend(ai_keywords)
                    print(f"   AI extracted {len(ai_keywords)} keywords from publications")
        
        # Step 3: AI extraction from thesis data (titles, content)
        print(" Step 3: AI extraction from thesis data...")
        if visitor_profile.get('thesis_data'):
            thesis_keywords = self.ai_extractor.extract_keywords_from_thesis_data(visitor_profile['thesis_data'])
            all_keywords.extend(thesis_keywords)
            print(f"   AI extracted {len(thesis_keywords)} keywords from thesis data")
        
        # Clean and deduplicate
        unique_keywords = list(set([kw.strip() for kw in all_keywords if kw and kw.strip()]))
        
        print(f" TOTAL: {len(unique_keywords)} comprehensive keywords extracted")
        return unique_keywords
    
    def _get_person_publications(self, person_name: str) -> list:
        """Get publications for a person for AI keyword extraction"""
        if not person_name:
            return []
            
        with self.db1_driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person)-[:AUTHORED]->(pub:Publication)
            WHERE p.name = $person_name
            RETURN pub.name as title, 
                   pub.Abstract as abstract,
                   pub.Keywords as existing_keywords
            LIMIT 10
            """
            
            try:
                result = session.run(query, person_name=person_name)
                publications = []
                for record in result:
                    # Handle None values safely
                    title = record.get('title') or ''
                    abstract = record.get('abstract') or ''
                    keywords = record.get('existing_keywords') or []
                    
                    # Convert to strings safely
                    if title and hasattr(title, 'strip'):
                        title = title.strip()
                    elif title is None:
                        title = ''
                    else:
                        title = str(title)
                    
                    if abstract and hasattr(abstract, 'strip'):
                        abstract = abstract.strip()
                    elif abstract is None:
                        abstract = ''
                    else:
                        abstract = str(abstract)
                        
                    if keywords is None:
                        keywords = []
                    elif isinstance(keywords, str):
                        keywords = [kw.strip() for kw in keywords.split(',') if kw.strip()]
                    elif not isinstance(keywords, list):
                        keywords = []
                    
                    pub_data = {
                        'name': title,
                        'abstract': abstract,
                        'keywords': keywords
                    }
                    publications.append(pub_data)
                return publications
            except Exception as e:
                print(f"⚠️ Error getting publications for {person_name}: {e}")
                return []
    
    def _find_project_collaborators(self, visitor_name: str, home_organization: str) -> list:
        """Find people who were funded by same projects as visitor"""
        with self.db1_driver.session(database="neo4j") as session:
            query = """
            // Find visitor's funded projects
            MATCH (visitor:Person)-[:FUNDED]->(proj:Project)<-[:FUNDED]-(colleague:Person)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND NOT toLower(colleague.name) CONTAINS toLower($visitor_name)
            
            // Check if colleague is from target organization
            MATCH (colleague)-[w:WORKED_AT]->(org:Organization)
            WHERE toLower(org.name) CONTAINS toLower($org_name)
            
            WITH colleague, proj,
                 count(DISTINCT proj) as shared_projects,
                 collect(DISTINCT proj.name)[..2] as project_names,
                 collect(DISTINCT w.department)[..2] as departments
            
            RETURN colleague.name as name,
                   colleague.orcid_id as orcid_id,
                   shared_projects,
                   project_names,
                   departments,
                   'project_collaboration' as relation_type
            ORDER BY shared_projects DESC
            LIMIT 3
            """
            
            result = session.run(query,
                               visitor_name=visitor_name,
                               org_name=home_organization)
            return [dict(record) for record in result]

    def _find_alumni_networks(self, visitor_name: str, home_organization: str) -> list:
        """Find people where visitor studied at same place they work"""
        with self.db1_driver.session(database="neo4j") as session:
            query = """
            // Find where visitor studied and who works there
            MATCH (visitor:Person)-[:STUDIED_AT]->(edu_org:Organization)<-[:WORKED_AT]-(colleague:Person)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND NOT toLower(colleague.name) CONTAINS toLower($visitor_name)
            
            // Check if colleague is also affiliated with target organization
            MATCH (colleague)-[w:WORKED_AT]->(target_org:Organization)
            WHERE toLower(target_org.name) CONTAINS toLower($org_name)
            
            WITH colleague, edu_org,
                 collect(DISTINCT w.department)[..2] as departments,
                 collect(DISTINCT w.role)[..2] as roles
            
            RETURN colleague.name as name,
                   colleague.orcid_id as orcid_id,
                   edu_org.name as shared_institution,
                   departments,
                   roles,
                   'alumni_network' as relation_type
            LIMIT 3
            """
            
            result = session.run(query,
                               visitor_name=visitor_name,
                               org_name=home_organization)
            return [dict(record) for record in result]

    def _find_industry_bridges(self, visitor_name: str, home_organization: str) -> list:
        """Find industry bridge connections through thesis supervision"""
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            // Find visitor's industry supervision connections
            MATCH (visitor:Person)-[r1]->(thesis:Thesis)<-[r2]-(colleague:Person)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND NOT toLower(colleague.name) CONTAINS toLower($visitor_name)
              AND (type(r1) CONTAINS 'INDUSTRY' OR type(r2) CONTAINS 'INDUSTRY' 
                   OR type(r1) = 'COMPANY_SUPERVISOR' OR type(r2) = 'COMPANY_SUPERVISOR')
            
            WITH colleague,
                 collect(DISTINCT type(r1)) as visitor_roles,
                 collect(DISTINCT type(r2)) as colleague_roles,
                 count(DISTINCT thesis) as shared_industry_theses,
                 collect(DISTINCT thesis.title)[..2] as sample_theses
            
            RETURN colleague.name as name,
                   visitor_roles,
                   colleague_roles,
                   shared_industry_theses,
                   sample_theses,
                   'industry_bridge' as relation_type
            ORDER BY shared_industry_theses DESC
            LIMIT 3
            """
            
            result = session.run(query, visitor_name=visitor_name)
            return [dict(record) for record in result]

    def _find_cross_database_topics(self, visitor_name: str, home_organization: str, visitor_keywords: list, limit: int) -> list:
        """Find cross-database topic matching (publication keywords ↔ thesis keywords)"""
        if not visitor_keywords:
            return []
            
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            // Find Chalmers people with thesis keywords matching visitor's publication keywords
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE any(keyword IN t.keywords 
                      WHERE any(visitor_kw IN $visitor_keywords 
                                WHERE toLower(keyword) CONTAINS toLower(visitor_kw)))
            
            WITH p, 
                 count(DISTINCT t) as matching_theses,
                 collect(DISTINCT type(r))[..2] as thesis_roles,
                 collect(DISTINCT t.title)[..1] as sample_thesis
            
            RETURN p.name as name,
                   matching_theses,
                   thesis_roles,
                   sample_thesis,
                   'cross_topic_matching' as relation_type
            ORDER BY matching_theses DESC
            LIMIT $limit
            """
            
            result = session.run(query,
                               visitor_keywords=visitor_keywords,
                               limit=limit)
            return [dict(record) for record in result]

    def _find_same_alma_mater(self, visitor_name: str, home_organization: str) -> list:
        """Find people who studied at the same institution as the visitor"""
        with self.db1_driver.session(database="neo4j") as session:
            query = """
            // Find where visitor studied
            MATCH (visitor:Person)-[:STUDIED_AT]->(edu:Organization)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND NOT toLower(edu.name) CONTAINS 'chalmers'  // Exclude Chalmers as alma mater
            
            // Find Chalmers people who studied at same place
            MATCH (colleague:Person)-[:STUDIED_AT]->(edu)
            MATCH (colleague)-[w:WORKED_AT]->(org:Organization)
            WHERE toLower(org.name) CONTAINS toLower($org_name)
              AND NOT toLower(colleague.name) CONTAINS toLower($visitor_name)
            
            WITH colleague, edu,
                 collect(DISTINCT w.department)[..2] as departments,
                 collect(DISTINCT w.role)[..2] as roles,
                 count(DISTINCT edu) as shared_institutions
            
            RETURN colleague.name as name,
                   colleague.orcid_id as orcid_id,
                   edu.name as shared_alma_mater,
                   departments,
                   roles,
                   shared_institutions,
                   'same_alma_mater' as relation_type
            ORDER BY shared_institutions DESC
            LIMIT 5
            """
            
            result = session.run(query,
                               visitor_name=visitor_name,
                               org_name=home_organization)
            return [dict(record) for record in result]
    
    def _find_keyword_similarity(self, visitor_name: str, home_organization: str, visitor_keywords: list, limit: int) -> list:
        """Find researchers with meaningful keyword similarity (requires multiple matches)"""
        with self.db1_driver.session(database="neo4j") as session:
            # Get all potential candidates first
            query = """
            MATCH (p:Person)-[w:WORKED_AT]->(org:Organization)
            WHERE toLower(org.name) CONTAINS toLower($org_name)
              AND NOT toLower(p.name) CONTAINS toLower($visitor_name)
            
            OPTIONAL MATCH (p)-[:AUTHORED]->(pub:Publication)
            
            WITH p, org,
                 collect(DISTINCT w.department) as departments,
                 collect(DISTINCT w.role) as roles,
                 count(pub) as publications,
                 p.orcid_keywords as keywords
            
            RETURN DISTINCT p.name as name,
                   p.orcid_id as orcid_id,
                   departments,
                   roles,
                   publications,
                   keywords,
                   org.name as organization
            """
            
            result = session.run(query,
                               org_name=home_organization,
                               visitor_name=visitor_name)
            
            candidates = [dict(record) for record in result]
            
            # Calculate comprehensive similarity in Python for better control
            similarity_matches = []
            
            for candidate in candidates:
                similarity_data = self._calculate_comprehensive_similarity(
                    visitor_keywords, 
                    candidate.get('keywords', '') or '',
                    candidate.get('departments', []) or [],
                    candidate.get('roles', []) or []
                )
                
                # Only include if meaningful similarity (multiple matches or high-quality single match)
                if similarity_data['is_meaningful']:
                    candidate.update(similarity_data)
                    similarity_matches.append(candidate)
            
            # Sort by comprehensive similarity score
            similarity_matches.sort(key=lambda x: (x['comprehensive_score'], x['publications']), reverse=True)
            
            return similarity_matches[:limit]
    
    def _calculate_comprehensive_similarity(self, visitor_keywords: list, candidate_keywords: str, departments: list, roles: list) -> dict:
        """Calculate comprehensive similarity score with quality filters"""
        
        # Define common/generic keywords that should have lower weight
        generic_keywords = {
            'innovation', 'research', 'development', 'analysis', 'study', 'investigation', 
            'engineering', 'technology', 'management', 'system', 'design', 'method',
            'sustainable', 'sustainability', 'green', 'environmental', 'digital',
            'artificial intelligence', 'machine learning', 'data', 'computer'
        }
        
        # Find exact matches
        orcid_matches = []
        dept_matches = []
        role_matches = []
        
        visitor_keywords_lower = [kw.lower().strip() for kw in visitor_keywords]
        candidate_keywords_lower = candidate_keywords.lower() if candidate_keywords else ''
        
        # ORCID keyword matching (exact phrase matching with punctuation handling)
        import re
        for visitor_kw in visitor_keywords:
            visitor_kw_clean = visitor_kw.lower().strip()
            if len(visitor_kw_clean) > 2:  # Skip very short keywords
                # Create regex pattern that matches word boundaries and punctuation
                # This handles cases like "machine learning," "machine learning;" etc.
                pattern = r'\b' + re.escape(visitor_kw_clean) + r'\b'
                if re.search(pattern, candidate_keywords_lower):
                    orcid_matches.append(visitor_kw)
        
        # Department matching
        for visitor_kw in visitor_keywords:
            visitor_kw_clean = visitor_kw.lower().strip()
            for dept in departments:
                if dept and visitor_kw_clean in dept.lower():
                    dept_matches.append(f"{visitor_kw} in {dept}")
        
        # Role matching  
        for visitor_kw in visitor_keywords:
            visitor_kw_clean = visitor_kw.lower().strip()
            for role in roles:
                if role and visitor_kw_clean in role.lower():
                    role_matches.append(f"{visitor_kw} in {role}")
        
        # Calculate weighted scores based on keyword quality
        orcid_score = 0
        high_quality_matches = []
        
        for match in orcid_matches:
            match_lower = match.lower().strip()
            if match_lower in generic_keywords:
                orcid_score += 1  # Lower weight for generic terms
            else:
                orcid_score += 3  # Full weight for specific terms
                high_quality_matches.append(match)
        
        dept_score = len(dept_matches) * 2
        role_score = len(role_matches) * 1
        
        total_matches = len(orcid_matches) + len(dept_matches) + len(role_matches)
        comprehensive_score = orcid_score + dept_score + role_score
        
        # Determine if this is meaningful similarity
        is_meaningful = False
        
        if total_matches >= 2:
            # Multiple matches = always meaningful
            is_meaningful = True
        elif len(high_quality_matches) >= 1:
            # Single high-quality (non-generic) match = meaningful
            is_meaningful = True
        elif comprehensive_score >= 4:
            # High score from dept/role matches = meaningful
            is_meaningful = True
        
        # Calculate percentage similarity
        if len(visitor_keywords) > 0:
            similarity_percentage = (len(orcid_matches) / len(visitor_keywords)) * 100
        else:
            similarity_percentage = 0
        
        return {
            'orcid_matches': orcid_matches,
            'dept_matches': dept_matches, 
            'role_matches': role_matches,
            'high_quality_matches': high_quality_matches,
            'total_matches': total_matches,
            'comprehensive_score': comprehensive_score,
            'similarity_percentage': round(similarity_percentage, 1),
            'is_meaningful': is_meaningful,
            'match_quality': 'high' if len(high_quality_matches) >= 1 else 'generic'
        }

    def _find_co_author_bridges(self, visitor_name: str, home_organization: str, limit: int) -> list:
        """Find co-author bridges: visitor X -> co-author Y -> Chalmers person Z"""
        with self.db1_driver.session(database="neo4j") as session:
            # Simplified query to avoid memory issues
            query = """
            // Find visitor's most prolific co-authors first (limit to reduce memory)
            MATCH (visitor:Person)-[:AUTHORED]->(pub1:Publication)<-[:AUTHORED]-(bridge:Person)
            WHERE toLower(visitor.name) CONTAINS toLower($visitor_name)
              AND NOT toLower(bridge.name) CONTAINS toLower($visitor_name)
            
            WITH bridge, count(pub1) as visitor_bridge_pubs
            ORDER BY visitor_bridge_pubs DESC
            LIMIT 10  // Only check top 10 bridges to avoid memory issues
            
            // Find Chalmers people who co-authored with these bridge people
            MATCH (bridge)-[:AUTHORED]->(pub2:Publication)<-[:AUTHORED]-(colleague:Person)
            MATCH (colleague)-[:WORKED_AT]->(org:Organization)
            WHERE toLower(org.name) CONTAINS toLower($org_name)
              AND NOT toLower(colleague.name) CONTAINS toLower($visitor_name)
              AND colleague <> bridge
            
            WITH colleague, bridge, 
                 visitor_bridge_pubs,
                 count(DISTINCT pub2) as bridge_colleague_pubs
            
            WITH colleague, 
                 collect(DISTINCT bridge.name) as bridge_people,
                 max(visitor_bridge_pubs) as visitor_bridge_pubs,
                 sum(bridge_colleague_pubs) as total_bridge_score
            
            RETURN DISTINCT colleague.name as name,
                   colleague.orcid_id as orcid_id,
                   bridge_people[0] as bridge_person,  // Primary bridge person
                   bridge_people as all_bridges,       // All bridge connections
                   visitor_bridge_pubs,
                   total_bridge_score,
                   'co_author_bridge' as relation_type
            ORDER BY total_bridge_score DESC
            LIMIT $limit
            """
            
            result = session.run(query,
                               visitor_name=visitor_name,
                               org_name=home_organization,
                               limit=limit)
            return [dict(record) for record in result]

    def smart_query_handler(self, user_input: str) -> dict:
        """
        RESEARCHBOOK SMART FEATURE: Universal Query Handler
        Route user queries to appropriate functions based on AI interpretation
        """
        print(f"🤖 Processing smart query: {user_input}")
        
        # Parse user intent
        intent = self.parse_user_intent(user_input)
        query_type = intent.get('query_type', 'general_search')
        entities = intent.get('entities', {})
        filters = intent.get('filters', {})
        
        try:
            # Route to appropriate function
            if query_type == 'meeting_recommendation':
                visitor = entities.get('visitor_name', entities.get('person_name'))
                home_org = entities.get('home_organization', 'Chalmers')
                output_format = intent.get('output_format', 'standard')
                
                # Store intent for exclusion parsing
                self._last_intent = intent
                
                result = self.strategic_meeting_recommendations(visitor, home_org, user_query=user_input, output_format=output_format)
                result['query_interpretation'] = intent
                return result
                
            elif query_type == 'expert_finder':
                topic = entities.get('research_topic', entities.get('search_term', ''))
                org_filter = filters.get('organization')
                result = self.find_expert_with_filters(topic, org_filter)
                result['query_interpretation'] = intent
                return result
                
            elif query_type == 'person_lookup':
                person_name = entities.get('person_name', entities.get('search_term', ''))
                result = self.lookup_person(person_name)
                result['query_interpretation'] = intent
                return result
                
            elif query_type == 'field_intelligence':
                field = entities.get('research_field', entities.get('research_topic', entities.get('search_term', '')))
                result = self.generate_field_brief(field)
                result['query_interpretation'] = intent
                return result
                
            elif query_type == 'researcher_matching':
                target = entities.get('person_name', entities.get('search_term', ''))
                result = self.match_researchers(target)
                result['query_interpretation'] = intent
                return result
                
            else:
                # Default to general search
                search_term = entities.get('search_term', user_input)
                result = self.find_expert(search_term, limit=8)
                result['query_interpretation'] = intent
                result['fallback_search'] = True
                return result
                
        except Exception as e:
            return {
                "error": f"Could not process query: {str(e)}",
                "query_interpretation": intent,
                "suggestion": "Please try rephrasing your question or use the specific search functions."
            }

    def find_expert_with_filters(self, topic: str, org_filter: str = None, limit: int = 10) -> dict:
        """
        Enhanced expert finder with organization filtering
        """
        print(f" Finding experts on: {topic}" + (f" at {org_filter}" if org_filter else ""))
        
        # Get experts from both databases
        db1_experts = self._get_db1_experts(topic, org_filter)
        db2_experts = self._get_db2_experts(topic)
        
        # Generate AI ranking with filter context
        ranking_prompt = f"""
        Rank and analyze experts for topic: "{topic}"
        {f"Specifically from organization: {org_filter}" if org_filter else ""}
        
        RESEARCH INTELLIGENCE EXPERTS:
        {json.dumps(db1_experts, indent=2)}
        
        ACADEMIC NETWORK EXPERTS:
        {json.dumps(db2_experts, indent=2)}
        
        Please provide:
        1. **Top Expert Rankings** - Best matches for "{topic}"
        {f"2. **{org_filter} Focus** - Why these {org_filter} researchers are ideal" if org_filter else "2. **Expert Analysis** - Why each expert is relevant"}
        3. **Collaboration Recommendations** - Who to contact for different needs
        4. **Strategic Insights** - Trends and opportunities in this expertise area
        
        Keep response focused and actionable.
        """
        
        ai_ranking = self.ai_query(ranking_prompt, max_tokens=1200)
        
        return {
            "topic": topic,
            "organization_filter": org_filter,
            "experts_found": len(db1_experts) + len(db2_experts),
            "research_intelligence_matches": len(db1_experts),
            "academic_network_matches": len(db2_experts),
            "expert_list": db1_experts + db2_experts,
            "ai_ranking": ai_ranking
        }

    def _get_db1_experts(self, topic: str, org_filter: str = None) -> list:
        """Get experts from Database 1 with optional organization filter"""
        with self.db1_driver.session(database="neo4j") as session:
            base_query = """
            MATCH (p:Person)-[:AUTHORED]->(pub:Publication)
            WHERE toLower(pub.title) CONTAINS toLower($topic)
            """
            
            if org_filter:
                base_query += """
                MATCH (p)-[:WORKED_AT]->(org:Organization)
                WHERE toLower(org.name) CONTAINS toLower($org_filter)
                """
            
            base_query += """
            WITH p, count(pub) as relevant_publications,
                 collect(pub.title)[..2] as sample_publications
            RETURN p.name as name, p.orcid_id as orcid_id,
                   relevant_publications, sample_publications,
                   'Research Intelligence' as source
            ORDER BY relevant_publications DESC
            LIMIT 8
            """
            
            params = {"topic": topic}
            if org_filter:
                params["org_filter"] = org_filter
                
            result = session.run(base_query, **params)
            return [dict(record) for record in result]

    def _get_db2_experts(self, topic: str) -> list:
        """Get experts from Database 2 (thesis ecosystem)"""
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE toLower(t.title) CONTAINS toLower($topic) OR
                  any(keyword IN t.keywords WHERE toLower(keyword) CONTAINS toLower($topic))
            WITH p, count(t) as relevant_theses,
                 collect(DISTINCT type(r)) as roles,
                 collect(t.title)[..2] as sample_work
            RETURN p.name as name, relevant_theses, roles, sample_work,
                   'Academic Network' as source
            ORDER BY relevant_theses DESC
            LIMIT 8
            """
            
            result = session.run(query, topic=topic)
            return [dict(record) for record in result]

    def match_researchers(self, researcher_name: str) -> dict:
        """
        RESEARCHBOOK CORE FEATURE 4: Researcher Matching (Simple)
        """
        print(f" Finding matches for: {researcher_name}")
        
        # Get target researcher's thesis involvement
        with self.db2_driver.session(database="neo4j") as session:
            # Get target's keywords
            target_query = """
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE toLower(p.name) CONTAINS toLower($name)
            WITH collect(t.keywords) as all_keywords
            UNWIND all_keywords as keyword_list
            UNWIND keyword_list as keyword
            RETURN collect(DISTINCT keyword) as unique_keywords
            LIMIT 1
            """
            
            target_result = session.run(target_query, name=researcher_name)
            target_record = target_result.single()
            
            if not target_record or not target_record["unique_keywords"]:
                # Fallback: Try to get keywords from Database 1 (publications)
                print(f" No thesis data found for {researcher_name}, trying publication data...")
                target_profile = self.lookup_person(researcher_name)
                
                if not target_profile["found_in_db1"]:
                    return {"error": f"No data found for {researcher_name} in either database"}
                
                # Extract keywords from researcher profile
                target_keywords = []
                for researcher in target_profile.get('researcher_data', []):
                    if researcher.get('orcid_keywords'):
                        target_keywords.extend(researcher['orcid_keywords'])
                
                if not target_keywords:
                    return {"error": f"No research keywords found for {researcher_name}"}
                    
                target_keywords = target_keywords[:10]  # Limit keywords
                print(f" Using publication keywords: {target_keywords[:3]}...")
            else:
                target_keywords = target_record["unique_keywords"][:10]
            
            # Find similar researchers
            match_query = """
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE any(keyword IN t.keywords WHERE keyword IN $keywords)
              AND NOT toLower(p.name) CONTAINS toLower($target_name)
            WITH p, count(t) as relevance,
                 collect(DISTINCT type(r)) as roles,
                 collect(t.title)[..2] as sample_work
            RETURN p.name as name, relevance, roles, sample_work
            ORDER BY relevance DESC
            LIMIT 10
            """
            
            match_result = session.run(match_query, 
                                     keywords=target_keywords, 
                                     target_name=researcher_name)
            raw_matches = [dict(record) for record in match_result]
            
            # Calculate similarity scores and match reasons
            matches = []
            for match in raw_matches:
                # Calculate similarity score based on relevance and keyword overlap
                relevance = match.get('relevance', 0)
                max_relevance = max([m.get('relevance', 1) for m in raw_matches])
                similarity_score = round((relevance / max_relevance) * 10, 1)
                
                # Generate match reasons
                match_reasons = []
                if relevance > 1:
                    match_reasons.append(f"High research overlap ({relevance} related projects)")
                if match.get('roles'):
                    roles = match['roles']
                    if 'SUPERVISOR' in roles:
                        match_reasons.append("Supervision experience")
                    if 'EXAMINER' in roles:
                        match_reasons.append("Examination expertise")
                if match.get('sample_work'):
                    match_reasons.append("Similar research areas")
                
                # Enhanced match record
                enhanced_match = {
                    'name': match['name'],
                    'relevance': relevance,
                    'similarity_score': similarity_score,
                    'match_reasons': match_reasons,
                    'roles': match.get('roles', []),
                    'sample_work': match.get('sample_work', [])
                }
                matches.append(enhanced_match)
        
        # Generate AI analysis
        ai_prompt = f"""
        Analyze researcher compatibility for: "{researcher_name}"
        
        Target researcher's keywords: {target_keywords}
        
        Potential matches:
        {json.dumps(matches, indent=2)}
        
        Provide:
        1. Top 5 recommended matches for collaboration
        2. Explanation of compatibility for each match
        3. Specific collaboration opportunities
        4. Match quality scores (1-10)
        
        Keep response concise but actionable.
        """
        
        ai_analysis = self.ai_query(ai_prompt, max_tokens=1000)
        
        return {
            "target_researcher": researcher_name,
            "target_keywords": target_keywords,
            "matches_found": len(matches),
            "potential_matches": matches,
            "ai_analysis": ai_analysis
        }
    
    def quick_demo(self):
        """Quick demonstration of all ResearchBook features"""
        print(" RESEARCHBOOK FULL DEMONSTRATION\n")
        
        # 1. Person Lookup
        print("1️ PERSON LOOKUP")
        person = self.lookup_person("Anders")
        print(f" Found {len(person['researcher_data'])} profiles in DB1, {len(person['thesis_data'])} activities in DB2")
        
        # 2. Expert Finder  
        print("\n2️ EXPERT FINDER")
        experts = self.find_expert("machine learning", limit=5)
        print(f" Found {experts['experts_found']} ML experts")
        
        # 3. Field Brief
        print("\n3️ FIELD INTELLIGENCE BRIEF")
        brief = self.generate_field_brief("sustainability")
        print(f" Generated brief for sustainability: {brief['researchers_found']} researchers")
        
        # 4. Researcher Matching
        print("\n4️ RESEARCHER MATCHING")
        matches = self.match_researchers("Anders")
        if "error" not in matches:
            print(f" Found {matches['matches_found']} potential matches")
        else:
            print(f" {matches['error']}")
        
        print(f"\n RESEARCHBOOK FEATURES WORKING:")
        print(f"    Person lookup across 2 databases")
        print(f"    Expert finding with AI ranking") 
        print(f"    Field intelligence briefs")
        print(f"    Researcher matching")
        print(f"    AI analysis for all features")
        
        return {
            "person_lookup": person,
            "expert_finder": experts,
            "field_brief": brief,
            "researcher_matching": matches
        }

if __name__ == "__main__":
    rb = ResearchBookFinal()
    
    # Run full demo
    demo_results = rb.quick_demo()
    
    print("\n" + "="*60)
    print(" RESEARCHBOOK IS FULLY FUNCTIONAL!")
    print("Your project vision is now reality with your 2 databases + LightLLM")
    
    rb.close_connections()



# topics:

# API integrations & robust REST use — ai_query(), calls from generate_field_brief() / find_expert_with_filters()
# Token auth, JSON payloads, timeouts, and error branches → same pattern for Slack/Figma/GitLab.

# Prompt engineering & LLM orchestration — generate_field_brief() / find_expert_with_filters() / match_researchers()
# Task-scoped prompts, token limits, structured outputs for downstream automation.

# LLM→JSON parsing hardening — parse_user_intent()
# Strips code fences, regexes JSON blocks, graceful fallback message when parsing fails.

# Intent parsing & routing — smart_query_handler() + parse_user_intent()
# Maps free text to actions (person_lookup, expert_finder, etc.) → just like chatbot command routing.

# Fuzzy name matching & normalization — _get_*_enhanced() using EnhancedNameMatcher.find_best_matches()
# Handles accents/hyphens/case + Jaccard/substring scoring → robust entity resolution from Slack queries.

# Graph queries & data fusion (Neo4j) — _find_co_authors(), _find_academic_network(), _find_keyword_similarity()
# Cypher across people/publications/theses; merges multi-source evidence for a single response.

# Rate/limit & memory safety — _find_co_author_bridges() (LIMITs, staged WITH), generate_field_brief() (truncate inputs)
# Pagination/limits prevent OOM and keep chatbot replies snappy.

# Similarity & ranking logic — _calculate_comprehensive_similarity()
# Weighted matches (generic vs specific terms), roles/departments → practical relevance scoring.

# Keyword extraction pipeline (AI + fallback) — _extract_comprehensive_keywords()
# Combines existing tags + AI extraction + dedupe → resilient metadata for search/compliance.

# Diversity-aware selection — _select_diverse_hard_relations() / _select_diverse_mjuk_relations()
# Round-robin/type-balanced picks → avoids repetitive recommendations in Slack summaries.

# Configurable filters & exclusions — _parse_relation_limits() + _last_intent.filters
# Parses “X hard / Y mjuk / exclude type” from user text → mirrors compliance filters (e.g., components).

# Explainable outputs — AI briefs in generate_field_brief() / match_researchers() and structured result formats
# Clear “why” reasoning and grouped views → compliance reports and stakeholder-friendly Slack posts.

# Graceful degradation — try/except around DB/LLM calls; fallback branches in _get_* and _extract_*
# Keeps the bot useful when an API or model hiccups (critical for production Slack assistants).

# Modular service design — class composition (EnhancedNameMatcher, AIKeywordExtractor), DB1/DB2 separation
# Swappable backends and clean boundaries → easy to add Slack/Figma/GitLab connectors.
