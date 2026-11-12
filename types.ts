export type CategoryResult = {
  category_id: string;
  name: string;
  weight_group: string;
  status: "experimental" | "reference_missing" | "unavailable" | string;
  score: number | null;
  explanation: string;
  confidence: number;
  distance?: number;
};

export type Analysis = {
  overall_score: number | null;
  analyzed_categories: number;
  coverage_percent: number;
  overall_confidence: number;
  categories: CategoryResult[];
  image_quality: {
    width: number;
    height: number;
    brightness: number;
    blur_variance: number;
    warnings: string[];
  };
  limitations: string[];
};
