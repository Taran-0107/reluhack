export interface Competitor {
  name: string;
  website: string | null;
  description: string;
}

export interface FieldMetadata<T> {
  value: T;
  source: string | null;
  confidence: number | null;
}

export interface ResearchResult {
  company_name: FieldMetadata<string>;
  website: FieldMetadata<string>;
  phone_number: FieldMetadata<string | null>;
  address: FieldMetadata<string | null>;
  products_services: FieldMetadata<string[]>;
  pain_points: FieldMetadata<string[]>;
  competitors: FieldMetadata<Competitor[]>;
  summary: FieldMetadata<string>;
}

export interface ResearchRequest {
  company_name?: string;
  website_url?: string;
  discord_bot_token?: string;
  discord_channel_id?: string;
  applicant_name?: string;
  applicant_email?: string;
}
