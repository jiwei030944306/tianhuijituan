import JSZip from 'jszip';

// --- Type Definitions ---
export interface ValidationTag {
  type: 'error' | 'warning' | 'success';
  label: string;
  message: string;
}

export interface ImportItem {
  id: string;
  originalId: string;
  stem: string;
  stemImages: string[];      // Raw paths from JSON (e.g., "images/q1.png")
  previewImages: string[];   // Blob URLs for display
  answer: string;
  analysis: string;
  tags: ValidationTag[];
  status: 'valid' | 'invalid';
  raw: QuestionRaw;
}

export interface ParseResult {
  items: ImportItem[];
  stats: {
    total: number;
    valid: number;
    invalid: number;
  };
  error?: string;
}

// Raw question shape extracted from the uploaded JSON. Keep it flexible but
// define a known subset to improve type-safety in downstream processing.
export interface QuestionRaw {
  id?: string;
  stem?: string;
  stemImages?: unknown[]; // keep loose as upstream data can vary
  answer?: string;
  analysis?: string;
  [key: string]: any;
}

// --- Validation Rules ---
const RULES = {
  MISSING_FIELD: { label: '格式错误', message: '缺少题干或答案' },
  MISSING_IMG: { label: '缺失图片', message: '引用的图片文件在压缩包中不存在' },
  VALID: { label: '校验通过', message: '数据格式正确' }
};

export class ZipParserService {
  /**
   * Parse a ZIP file and validate its content
   * @param file The uploaded ZIP file
   * @returns ParseResult with validated items
   */
  static async parse(file: File): Promise<ParseResult> {
    const zip = new JSZip();
    const result: ParseResult = {
      items: [],
      stats: { total: 0, valid: 0, invalid: 0 }
    };

    try {
      // 1. Load ZIP
      const content = await zip.loadAsync(file);
      
      // 2. Find JSON file
      const jsonFile = Object.values(content.files).find(f => f.name.endsWith('.json'));
      if (!jsonFile) {
        return { ...result, error: '未找到JSON数据文件 (questions.json)' };
      }

      // 3. Parse JSON
      const jsonStr = await jsonFile.async('string');
      let questions: QuestionRaw[];
      try {
        questions = JSON.parse(jsonStr);
        if (!Array.isArray(questions)) throw new Error('Root is not an array');
      } catch (e) {
        return { ...result, error: 'JSON文件格式错误' };
      }

      // 4. Create Image Map (Path -> Blob URL)
      // We do this first to make validation efficient
      const imageMap = new Map<string, string>();
      const imageFiles = Object.values(content.files).filter(f => 
        /\.(png|jpg|jpeg|gif|bmp)$/i.test(f.name)
      );
      
      for (const imgFile of imageFiles) {
        const blob = await imgFile.async('blob');
        const url = URL.createObjectURL(blob);
        imageMap.set(imgFile.name, url); // Store by full path in zip
      }

      // 5. Process & Validate Items
      for (const q of questions) {
        const item: ImportItem = {
          id: crypto.randomUUID(), // Temp ID for frontend
          originalId: q.id || 'unknown',
          stem: q.stem || '',
          stemImages: q.stemImages || [],
          previewImages: [],
          answer: q.answer || '',
          analysis: q.analysis || '',
          tags: [],
          status: 'valid', // Default valid
          raw: q
        };

        // Rule 1: Missing Required Fields
        if (!item.stem || !item.answer) {
          item.tags.push({ type: 'error', ...RULES.MISSING_FIELD });
          item.status = 'invalid';
        }

        // Rule 2: Image Reference Integrity
        for (const imgPath of item.stemImages) {
          if (imageMap.has(imgPath)) {
            item.previewImages.push(imageMap.get(imgPath)!);
          } else {
            // Try lenient matching (if path has ./ or different slash)
            // Ideally we stick to exact match, but let's be strict for now
            item.tags.push({ 
              type: 'error', 
              label: RULES.MISSING_IMG.label, 
              message: `${RULES.MISSING_IMG.message}: ${imgPath}` 
            });
            item.status = 'invalid';
            // Add a placeholder for broken image? Maybe later.
          }
        }

        // Final Status Check
        if (item.status === 'valid') {
          item.tags.push({ type: 'success', ...RULES.VALID });
          result.stats.valid++;
        } else {
          result.stats.invalid++;
        }

        result.items.push(item);
      }

      result.stats.total = questions.length;
      return result;

    } catch (e) {
      console.error('Zip Parse Error:', e);
      return { ...result, error: '解析ZIP文件失败: ' + (e as Error).message };
    }
  }

  /**
   * Clean up Blob URLs to prevent memory leaks
   */
  static revokeUrls(items: ImportItem[]) {
    const urlsToRevoke = new Set<string>();
    items.forEach(item => {
      item.previewImages.forEach(url => urlsToRevoke.add(url));
    });
    urlsToRevoke.forEach(url => URL.revokeObjectURL(url));
  }
}
