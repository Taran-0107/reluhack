export interface Competitor {
  name: string;
  website: string | null;
  description: string;
}

export interface ResearchResult {
  company_name: string;
  website: string;
  phone_number: string | null;
  address: string | null;
  products_services: string[];
  pain_points: string[];
  competitors: Competitor[];
  summary: string;
}

export interface ResearchRequest {
  company_name?: string;
  website_url?: string;
  discord_bot_token?: string;
  discord_channel_id?: string;
  applicant_name?: string;
  applicant_email?: string;
}
