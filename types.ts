export type CategoryResult = {
  category_id: string;
  name: string;
  weight_group: string;
  score: number | null;
  confidence: number;
  distance?: number | null;
  status: "experimental" | "reference_missing" | "not_assessable";
  explanation: string;
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
