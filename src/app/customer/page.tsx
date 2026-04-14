"use client";

import { useState, useMemo } from "react";
import {
  Factory,
  CheckCircle,
  ChevronRight,
  ChevronLeft,
  Package,
  Settings,
  FileText,
  User,
  CircleCheck,
  Paintbrush,
  ShieldCheck,
  Layers,
  Stamp,
  Image,
  Ruler,
  Weight,
  Gem,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { SmartCastHeader } from "@/components/SmartCastHeader";

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

type ProductId = string;
type Category = "all" | "round" | "square" | "oval";

interface Product {
  id: ProductId;
  name: string;
  category: Category;
  categoryLabel: string;
  spec: string;
  priceRange: string;
  basePrice: number;
  diameterOptions: string[];
  thicknessOptions: string[];
  materials: string[];
  loadClassRange: string;
}

interface FormData {
  // Step 1
  selectedProduct: ProductId | null;
  // Step 2
  diameter: string;
  thickness: string;
  loadClass: string;
  material: string;
  postProcessing: string[];
  quantity: number;
  desiredDelivery: string;
  // Step 4
  companyName: string;
  contactPerson: string;
  phone: string;
  email: string;
  address: string;
}

// ─────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────

const CATEGORIES: { id: Category; label: string }[] = [
  { id: "all", label: "전체" },
  { id: "round", label: "원형 맨홀뚜껑" },
  { id: "square", label: "사각 맨홀뚜껑" },
  { id: "oval", label: "타원형 맨홀뚜껑" },
];

// @MX:NOTE: 카테고리별 제품 대표 이미지. "all"은 렌더링에 사용되지 않음.
const CATEGORY_IMAGES: Record<Exclude<Category, "all">, string> = {
  round: "/products/round.jpg",
  square: "/products/square.jpg",
  oval: "/products/oval.jpg",
};

// @MX:NOTE: 국내 주물 제조사(기남주물 외) 표준 KS 규격 맨홀뚜껑 제품군 30종.
// 원형(round) / 사각(square) / 타원형(oval) 각 10종. 가격은 기준가(basePrice)로
// 후처리 옵션 추가 시 합산됨.
const PRODUCTS: Product[] = [
  // ─── 원형 맨홀뚜껑 (10종) ───
  {
    id: "R-D450",
    name: "원형 맨홀뚜껑 KS D-450",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 450mm, KS 규격",
    priceRange: "75,000원",
    basePrice: 75000,
    diameterOptions: ["450mm"],
    thicknessOptions: ["25mm", "30mm", "35mm", "40mm"],
    materials: ["FC200", "FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "R-D500",
    name: "원형 맨홀뚜껑 KS D-500",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 500mm, KS 규격",
    priceRange: "82,000원",
    basePrice: 82000,
    diameterOptions: ["500mm"],
    thicknessOptions: ["25mm", "30mm", "35mm", "40mm"],
    materials: ["FC200", "FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "R-D550",
    name: "원형 맨홀뚜껑 KS D-550",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 550mm, KS 규격",
    priceRange: "90,000원",
    basePrice: 90000,
    diameterOptions: ["550mm"],
    thicknessOptions: ["30mm", "35mm", "40mm"],
    materials: ["FC200", "FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "R-D600",
    name: "원형 맨홀뚜껑 KS D-600",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 600mm, KS 규격",
    priceRange: "98,000원",
    basePrice: 98000,
    diameterOptions: ["600mm"],
    thicknessOptions: ["30mm", "35mm", "40mm", "45mm"],
    materials: ["FC200", "FC250", "GCD450", "GCD500"],
    loadClassRange: "B125 ~ F900",
  },
  {
    id: "R-D650",
    name: "원형 맨홀뚜껑 KS D-650",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 650mm, KS 규격",
    priceRange: "108,000원",
    basePrice: 108000,
    diameterOptions: ["650mm"],
    thicknessOptions: ["30mm", "35mm", "40mm", "45mm"],
    materials: ["FC250", "GCD450", "GCD500"],
    loadClassRange: "C250 ~ F900",
  },
  {
    id: "R-D700",
    name: "원형 맨홀뚜껑 KS D-700",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 700mm, KS 규격",
    priceRange: "118,000원",
    basePrice: 118000,
    diameterOptions: ["700mm"],
    thicknessOptions: ["35mm", "40mm", "45mm", "50mm"],
    materials: ["FC250", "GCD450", "GCD500"],
    loadClassRange: "C250 ~ F900",
  },
  {
    id: "R-D750",
    name: "원형 맨홀뚜껑 KS D-750",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 750mm, KS 규격",
    priceRange: "128,000원",
    basePrice: 128000,
    diameterOptions: ["750mm"],
    thicknessOptions: ["35mm", "40mm", "45mm", "50mm"],
    materials: ["FC250", "GCD450", "GCD500"],
    loadClassRange: "C250 ~ F900",
  },
  {
    id: "R-D800",
    name: "원형 맨홀뚜껑 KS D-800",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 800mm, KS 규격",
    priceRange: "138,000원",
    basePrice: 138000,
    diameterOptions: ["800mm"],
    thicknessOptions: ["35mm", "40mm", "45mm", "50mm"],
    materials: ["FC250", "GCD450", "GCD500"],
    loadClassRange: "C250 ~ F900",
  },
  {
    id: "R-D850",
    name: "원형 맨홀뚜껑 KS D-850",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 850mm, KS 규격",
    priceRange: "152,000원",
    basePrice: 152000,
    diameterOptions: ["850mm"],
    thicknessOptions: ["40mm", "45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },
  {
    id: "R-D900",
    name: "원형 맨홀뚜껑 KS D-900",
    category: "round",
    categoryLabel: "원형 맨홀뚜껑",
    spec: "직경 900mm, KS 규격",
    priceRange: "165,000원",
    basePrice: 165000,
    diameterOptions: ["900mm"],
    thicknessOptions: ["40mm", "45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },

  // ─── 사각 맨홀뚜껑 (10종) ───
  {
    id: "S-400",
    name: "사각 맨홀뚜껑 KS S-400",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "400x400mm, KS 규격",
    priceRange: "68,000원",
    basePrice: 68000,
    diameterOptions: ["400x400mm"],
    thicknessOptions: ["25mm", "30mm", "35mm"],
    materials: ["FC200", "FC250"],
    loadClassRange: "A15 ~ C250",
  },
  {
    id: "S-450",
    name: "사각 맨홀뚜껑 KS S-450",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "450x450mm, KS 규격",
    priceRange: "78,000원",
    basePrice: 78000,
    diameterOptions: ["450x450mm"],
    thicknessOptions: ["25mm", "30mm", "35mm", "40mm"],
    materials: ["FC200", "FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "S-500",
    name: "사각 맨홀뚜껑 KS S-500",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "500x500mm, KS 규격",
    priceRange: "88,000원",
    basePrice: 88000,
    diameterOptions: ["500x500mm"],
    thicknessOptions: ["30mm", "35mm", "40mm"],
    materials: ["FC200", "FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "S-550",
    name: "사각 맨홀뚜껑 KS S-550",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "550x550mm, KS 규격",
    priceRange: "98,000원",
    basePrice: 98000,
    diameterOptions: ["550x550mm"],
    thicknessOptions: ["30mm", "35mm", "40mm"],
    materials: ["FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "S-600",
    name: "사각 맨홀뚜껑 KS S-600",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "600x600mm, KS 규격",
    priceRange: "108,000원",
    basePrice: 108000,
    diameterOptions: ["600x600mm"],
    thicknessOptions: ["30mm", "35mm", "40mm", "45mm"],
    materials: ["FC250", "GCD450", "GCD500"],
    loadClassRange: "C250 ~ F900",
  },
  {
    id: "S-650",
    name: "사각 맨홀뚜껑 KS S-650",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "650x650mm, KS 규격",
    priceRange: "118,000원",
    basePrice: 118000,
    diameterOptions: ["650x650mm"],
    thicknessOptions: ["35mm", "40mm", "45mm"],
    materials: ["FC250", "GCD450", "GCD500"],
    loadClassRange: "C250 ~ F900",
  },
  {
    id: "S-700",
    name: "사각 맨홀뚜껑 KS S-700",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "700x700mm, KS 규격",
    priceRange: "128,000원",
    basePrice: 128000,
    diameterOptions: ["700x700mm"],
    thicknessOptions: ["35mm", "40mm", "45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "C250 ~ F900",
  },
  {
    id: "S-750",
    name: "사각 맨홀뚜껑 KS S-750",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "750x750mm, KS 규격",
    priceRange: "138,000원",
    basePrice: 138000,
    diameterOptions: ["750x750mm"],
    thicknessOptions: ["40mm", "45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },
  {
    id: "S-800",
    name: "사각 맨홀뚜껑 KS S-800",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "800x800mm, KS 규격",
    priceRange: "148,000원",
    basePrice: 148000,
    diameterOptions: ["800x800mm"],
    thicknessOptions: ["40mm", "45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },
  {
    id: "S-900",
    name: "사각 맨홀뚜껑 KS S-900",
    category: "square",
    categoryLabel: "사각 맨홀뚜껑",
    spec: "900x900mm, KS 규격",
    priceRange: "168,000원",
    basePrice: 168000,
    diameterOptions: ["900x900mm"],
    thicknessOptions: ["45mm", "50mm", "55mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },

  // ─── 타원형 맨홀뚜껑 (10종) ───
  {
    id: "O-450",
    name: "타원형 맨홀뚜껑 KS O-450",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "450x300mm, KS 규격",
    priceRange: "72,000원",
    basePrice: 72000,
    diameterOptions: ["450x300mm"],
    thicknessOptions: ["25mm", "30mm", "35mm"],
    materials: ["FC200", "FC250"],
    loadClassRange: "A15 ~ C250",
  },
  {
    id: "O-500",
    name: "타원형 맨홀뚜껑 KS O-500",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "500x350mm, KS 규격",
    priceRange: "80,000원",
    basePrice: 80000,
    diameterOptions: ["500x350mm"],
    thicknessOptions: ["25mm", "30mm", "35mm"],
    materials: ["FC200", "FC250"],
    loadClassRange: "A15 ~ C250",
  },
  {
    id: "O-550",
    name: "타원형 맨홀뚜껑 KS O-550",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "550x400mm, KS 규격",
    priceRange: "88,000원",
    basePrice: 88000,
    diameterOptions: ["550x400mm"],
    thicknessOptions: ["30mm", "35mm", "40mm"],
    materials: ["FC200", "FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "O-600",
    name: "타원형 맨홀뚜껑 KS O-600",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "600x450mm, KS 규격",
    priceRange: "98,000원",
    basePrice: 98000,
    diameterOptions: ["600x450mm"],
    thicknessOptions: ["30mm", "35mm", "40mm"],
    materials: ["FC200", "FC250", "GCD450"],
    loadClassRange: "B125 ~ D400",
  },
  {
    id: "O-650",
    name: "타원형 맨홀뚜껑 KS O-650",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "650x500mm, KS 규격",
    priceRange: "108,000원",
    basePrice: 108000,
    diameterOptions: ["650x500mm"],
    thicknessOptions: ["35mm", "40mm", "45mm"],
    materials: ["FC250", "GCD450"],
    loadClassRange: "C250 ~ D400",
  },
  {
    id: "O-700",
    name: "타원형 맨홀뚜껑 KS O-700",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "700x550mm, KS 규격",
    priceRange: "118,000원",
    basePrice: 118000,
    diameterOptions: ["700x550mm"],
    thicknessOptions: ["35mm", "40mm", "45mm"],
    materials: ["FC250", "GCD450", "GCD500"],
    loadClassRange: "C250 ~ D400",
  },
  {
    id: "O-750",
    name: "타원형 맨홀뚜껑 KS O-750",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "750x600mm, KS 규격",
    priceRange: "128,000원",
    basePrice: 128000,
    diameterOptions: ["750x600mm"],
    thicknessOptions: ["40mm", "45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },
  {
    id: "O-800",
    name: "타원형 맨홀뚜껑 KS O-800",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "800x650mm, KS 규격",
    priceRange: "140,000원",
    basePrice: 140000,
    diameterOptions: ["800x650mm"],
    thicknessOptions: ["40mm", "45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },
  {
    id: "O-850",
    name: "타원형 맨홀뚜껑 KS O-850",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "850x700mm, KS 규격",
    priceRange: "152,000원",
    basePrice: 152000,
    diameterOptions: ["850x700mm"],
    thicknessOptions: ["45mm", "50mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "D400 ~ F900",
  },
  {
    id: "O-900",
    name: "타원형 맨홀뚜껑 KS O-900",
    category: "oval",
    categoryLabel: "타원형 맨홀뚜껑",
    spec: "900x750mm, KS 규격",
    priceRange: "168,000원",
    basePrice: 168000,
    diameterOptions: ["900x750mm"],
    thicknessOptions: ["45mm", "50mm", "55mm"],
    materials: ["GCD450", "GCD500"],
    loadClassRange: "E600 ~ F900",
  },
];

const LOAD_CLASSES = ["EN124 B125", "EN124 C250", "EN124 D400", "EN124 E600", "EN124 F900"];
const MATERIALS = ["FC200", "FC250", "GCD450", "GCD500"];

// ─────────────────────────────────────────────
// 이메일 검증 (Step 4 주문자 정보)
// ─────────────────────────────────────────────
// 실용적인 이메일 정규식:
//   - 로컬 파트: @/공백 제외 1자 이상
//   - @ 1 개
//   - 도메인: @/공백/쩜 제외 1자 이상 + "." + 2자 이상 TLD
//   - 연속 점(..) 금지, 점으로 시작/끝 금지
// RFC 5322 완벽 호환은 아니지만 99% 실 사용 케이스를 잡는다.
const EMAIL_REGEX =
  /^(?!\.)(?!.*\.\.)[^\s@.]+(?:\.[^\s@.]+)*@[^\s@.]+(?:\.[^\s@.]+)*\.[^\s@.]{2,}$/;

/** 이메일 형식이 유효한지 검사 (공백 자동 trim). */
export function isValidEmail(value: string): boolean {
  const trimmed = value.trim();
  if (trimmed.length === 0) return false;
  if (trimmed.length > 254) return false; // RFC 5321 권장 상한
  return EMAIL_REGEX.test(trimmed);
}

/** 사용자 친화적인 이메일 에러 메시지. 빈 값은 "필수" 아닌 "형식" 메시지만 담당. */
function emailErrorMessage(value: string): string | null {
  const trimmed = value.trim();
  if (trimmed.length === 0) return null; // 필수 검사와 분리
  if (!trimmed.includes("@")) return "이메일에 '@' 가 포함되어야 합니다.";
  const [local, domain] = trimmed.split("@");
  if (!local) return "'@' 앞에 사용자 이름이 필요합니다.";
  if (!domain) return "'@' 뒤에 도메인이 필요합니다.";
  if (!domain.includes(".")) return "도메인에 '.' 이 포함되어야 합니다 (예: gmail.com).";
  if (trimmed.length > 254) return "이메일이 너무 깁니다 (254자 이하).";
  if (!EMAIL_REGEX.test(trimmed)) return "올바른 이메일 주소 형식이 아닙니다.";
  return null;
}

const POST_PROCESSING_OPTIONS = [
  {
    id: "polish",
    label: "표면 연마",
    description: "매끄러운 표면 처리로 외관 품질 향상",
    price: 5000,
    icon: Paintbrush,
  },
  {
    id: "rustProof",
    label: "방청 코팅",
    description: "부식 방지 코팅으로 내구성 강화",
    price: 3000,
    icon: ShieldCheck,
  },
  {
    id: "zinc",
    label: "아연 도금",
    description: "아연 도금 처리로 장기 부식 방지",
    price: 8000,
    icon: Layers,
  },
  {
    id: "logo",
    label: "로고/문구 삽입",
    description: "회사 로고 또는 식별 문구 양각 삽입",
    price: 7000,
    icon: Stamp,
  },
];

const STEPS = [
  { id: 1, label: "주문자 정보", icon: User },
  { id: 2, label: "제품 선택", icon: Package },
  { id: 3, label: "사양 입력", icon: Settings },
  { id: 4, label: "견적 확인", icon: FileText },
  { id: 5, label: "주문 완료", icon: CircleCheck },
];

// ─────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("ko-KR").format(amount) + "원";
}

function generateOrderNumber(): string {
  const year = new Date().getFullYear();
  const seq = Math.floor(Math.random() * 900) + 100;
  return `ORD-${year}-${seq.toString().padStart(3, "0")}`;
}

// ─────────────────────────────────────────────
// Step Indicator Component
// ─────────────────────────────────────────────

function StepIndicator({ currentStep }: { currentStep: number }) {
  return (
    <div className="flex items-center justify-center mb-8">
      {STEPS.map((step, index) => {
        const Icon = step.icon;
        const isCompleted = step.id < currentStep;
        const isActive = step.id === currentStep;

        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                  isCompleted
                    ? "bg-blue-600 text-white"
                    : isActive
                    ? "bg-blue-600 text-white ring-4 ring-blue-100"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                {isCompleted ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <Icon className="w-5 h-5" />
                )}
              </div>
              <span
                className={`mt-1 text-xs font-medium whitespace-nowrap ${
                  isActive ? "text-blue-600" : isCompleted ? "text-gray-600" : "text-gray-400"
                }`}
              >
                {step.label}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div
                className={`w-12 sm:w-20 h-0.5 mx-1 mb-5 transition-all ${
                  step.id < currentStep ? "bg-blue-600" : "bg-gray-200"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─────────────────────────────────────────────
// Step 1: Product Selection (카테고리 필터 + 재질/하중등급)
// ─────────────────────────────────────────────

function Step1ProductSelection({
  selectedProduct,
  onSelect,
}: {
  selectedProduct: ProductId | null;
  onSelect: (id: ProductId) => void;
}) {
  const [category, setCategory] = useState<Category>("all");

  const filteredProducts = useMemo(() => {
    if (category === "all") return PRODUCTS;
    return PRODUCTS.filter((p) => p.category === category);
  }, [category]);

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-2">제품 선택</h2>
      <p className="text-sm text-gray-500 mb-6">주문하실 제품을 선택해 주세요.</p>

      {/* 카테고리 필터 */}
      <div className="flex items-center gap-2 mb-6">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setCategory(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              category === cat.id
                ? "bg-blue-600 text-white shadow-sm"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* 제품 그리드 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {filteredProducts.map((product) => {
          const isSelected = selectedProduct === product.id;
          return (
            <button
              key={product.id}
              onClick={() => onSelect(product.id)}
              className={`text-left rounded-xl border-2 p-5 transition-all hover:shadow-md ${
                isSelected
                  ? "border-blue-600 bg-blue-50 shadow-md"
                  : "border-gray-200 bg-white hover:border-blue-300"
              }`}
            >
              {/* 제품 이미지 (카테고리별 대표 이미지) */}
              <div className="w-full h-36 bg-white rounded-lg mb-4 relative overflow-hidden">
                {product.category !== "all" && CATEGORY_IMAGES[product.category] ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={CATEGORY_IMAGES[product.category]}
                    alt={product.name}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center">
                    <Factory
                      className={`w-10 h-10 mb-1 ${isSelected ? "text-blue-500" : "text-gray-400"}`}
                    />
                    <span className="text-xs text-gray-400">제품 이미지</span>
                  </div>
                )}
                {/* 카테고리 뱃지 */}
                <span className="absolute top-2 left-2 px-2 py-0.5 rounded-full text-[10px] font-medium bg-white/80 text-gray-700 border border-gray-200 backdrop-blur">
                  {product.categoryLabel}
                </span>
              </div>

              <h3 className={`font-semibold text-sm mb-1 ${isSelected ? "text-blue-700" : "text-gray-900"}`}>
                {product.name}
              </h3>
              <p className="text-xs text-gray-500 mb-3">{product.spec}</p>

              {/* 재질 + 하중등급 정보 */}
              <div className="space-y-1.5 mb-3">
                <div className="flex items-center gap-1.5 text-xs text-gray-500">
                  <Gem className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                  <span>재질: {product.materials.join(", ")}</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-gray-500">
                  <Weight className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                  <span>하중: {product.loadClassRange}</span>
                </div>
              </div>

              <p className={`text-xs font-medium ${isSelected ? "text-blue-600" : "text-gray-400"}`}>
                기준가 {product.priceRange}
              </p>
              {isSelected && (
                <div className="mt-3 flex items-center gap-1 text-blue-600">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-xs font-medium">선택됨</span>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Step 2: Specification Input (이미지 카드형 후처리)
// ─────────────────────────────────────────────

function Step2SpecInput({
  formData,
  product,
  onChange,
  errors,
}: {
  formData: FormData;
  product: Product;
  onChange: (field: keyof FormData, value: string | string[] | number) => void;
  errors: Partial<Record<keyof FormData, string>>;
}) {
  function togglePostProcessing(id: string) {
    const current = formData.postProcessing;
    const next = current.includes(id) ? current.filter((x) => x !== id) : [...current, id];
    onChange("postProcessing", next);
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-2">사양 입력</h2>
      <p className="text-sm text-gray-500 mb-6">선택하신 제품의 상세 사양을 입력해 주세요.</p>

      {/* 선택 제품 정보 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 mb-6 flex items-center gap-3">
        <Factory className="w-5 h-5 text-blue-600 shrink-0" />
        <div>
          <p className="text-sm font-semibold text-blue-800">{product.name}</p>
          <p className="text-xs text-blue-600">{product.spec}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {/* 규격 (직경) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            규격 (직경) <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.diameter}
            onChange={(e) => onChange("diameter", e.target.value)}
            className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.diameter ? "border-red-400 bg-red-50" : "border-gray-300"
            }`}
          >
            <option value="">선택하세요</option>
            {product.diameterOptions.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          {errors.diameter && <p className="mt-1 text-xs text-red-500">{errors.diameter}</p>}
        </div>

        {/* 두께 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            두께 <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.thickness}
            onChange={(e) => onChange("thickness", e.target.value)}
            className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.thickness ? "border-red-400 bg-red-50" : "border-gray-300"
            }`}
          >
            <option value="">선택하세요</option>
            {product.thicknessOptions.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          {errors.thickness && <p className="mt-1 text-xs text-red-500">{errors.thickness}</p>}
        </div>

        {/* 하중 등급 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            하중 등급 <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.loadClass}
            onChange={(e) => onChange("loadClass", e.target.value)}
            className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.loadClass ? "border-red-400 bg-red-50" : "border-gray-300"
            }`}
          >
            <option value="">선택하세요</option>
            {LOAD_CLASSES.map((cls) => (
              <option key={cls} value={cls}>{cls}</option>
            ))}
          </select>
          {errors.loadClass && <p className="mt-1 text-xs text-red-500">{errors.loadClass}</p>}
        </div>

        {/* 재질 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            재질 <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.material}
            onChange={(e) => onChange("material", e.target.value)}
            className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.material ? "border-red-400 bg-red-50" : "border-gray-300"
            }`}
          >
            <option value="">선택하세요</option>
            {MATERIALS.map((mat) => (
              <option key={mat} value={mat}>{mat}</option>
            ))}
          </select>
          {errors.material && <p className="mt-1 text-xs text-red-500">{errors.material}</p>}
        </div>

        {/* 수량 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            수량 (최소 10개) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            min={10}
            value={formData.quantity}
            onChange={(e) => onChange("quantity", Number(e.target.value))}
            className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.quantity ? "border-red-400 bg-red-50" : "border-gray-300"
            }`}
          />
          {errors.quantity && <p className="mt-1 text-xs text-red-500">{errors.quantity}</p>}
        </div>

        {/* 희망 납기일 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            희망 납기일 <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={formData.desiredDelivery}
            onChange={(e) => onChange("desiredDelivery", e.target.value)}
            min={new Date().toISOString().split("T")[0]}
            className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.desiredDelivery ? "border-red-400 bg-red-50" : "border-gray-300"
            }`}
          />
          {errors.desiredDelivery && (
            <p className="mt-1 text-xs text-red-500">{errors.desiredDelivery}</p>
          )}
        </div>
      </div>

      {/* 후처리 — 이미지 카드 형식 */}
      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">후처리 옵션 (선택)</label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {POST_PROCESSING_OPTIONS.map((opt) => {
            const isChecked = formData.postProcessing.includes(opt.id);
            const Icon = opt.icon;
            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => togglePostProcessing(opt.id)}
                className={`relative flex flex-col items-center text-center rounded-xl border-2 p-4 transition-all ${
                  isChecked
                    ? "border-blue-500 bg-blue-50 shadow-sm"
                    : "border-gray-200 bg-white hover:border-blue-300 hover:shadow-sm"
                }`}
              >
                {/* 아이콘 이미지 영역 */}
                <div
                  className={`w-14 h-14 rounded-xl flex items-center justify-center mb-3 ${
                    isChecked ? "bg-blue-100" : "bg-gray-100"
                  }`}
                >
                  <Icon className={`w-7 h-7 ${isChecked ? "text-blue-600" : "text-gray-400"}`} />
                </div>
                <p className={`text-xs font-semibold mb-1 ${isChecked ? "text-blue-700" : "text-gray-800"}`}>
                  {opt.label}
                </p>
                <p className="text-[10px] text-gray-400 leading-tight mb-2">{opt.description}</p>
                <span className={`text-xs font-medium ${isChecked ? "text-blue-600" : "text-gray-500"}`}>
                  +{formatCurrency(opt.price)}
                </span>
                {/* 선택 표시 */}
                {isChecked && (
                  <div className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-3.5 h-3.5 text-white" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Step 3: Quote Review (디자인 시안 + 옵션 미리보기)
// ─────────────────────────────────────────────

function Step3QuoteReview({
  formData,
  product,
}: {
  formData: FormData;
  product: Product;
}) {
  const postProcessingTotal = formData.postProcessing.reduce((sum, id) => {
    const opt = POST_PROCESSING_OPTIONS.find((o) => o.id === id);
    return sum + (opt?.price ?? 0);
  }, 0);
  const unitPrice = product.basePrice + postProcessingTotal;
  const totalPrice = unitPrice * formData.quantity;

  const selectedPostProcessing = POST_PROCESSING_OPTIONS.filter((opt) =>
    formData.postProcessing.includes(opt.id)
  );

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-2">견적 확인</h2>
      <p className="text-sm text-gray-500 mb-6">주문 내용과 디자인 시안을 확인해 주세요.</p>

      <div className="space-y-4">
        {/* 디자인 시안 + 옵션 미리보기 */}
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Image className="w-4 h-4 text-blue-600" />
            디자인 시안 미리보기
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* 디자인 시안 이미지 */}
            <div className="bg-gray-50 rounded-xl border border-gray-200 p-6 flex flex-col items-center justify-center min-h-[200px]">
              {product.category !== "all" && CATEGORY_IMAGES[product.category] ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={CATEGORY_IMAGES[product.category]}
                  alt={product.name}
                  className="w-32 h-32 object-contain mb-3"
                />
              ) : (
                <div className="w-28 h-28 bg-gray-200 rounded-full flex items-center justify-center mb-3">
                  <Factory className="w-14 h-14 text-gray-400" />
                </div>
              )}
              <p className="text-sm font-medium text-gray-700">{product.name}</p>
              <p className="text-xs text-gray-400 mt-1">기본 디자인 시안</p>
              <div className="mt-3 flex items-center gap-1.5 text-xs text-gray-400">
                <Ruler className="w-3 h-3" />
                <span>{formData.diameter} / {formData.thickness}</span>
              </div>
            </div>

            {/* 선택 옵션 요약 카드 */}
            <div className="space-y-3">
              {/* 규격 사양 */}
              <div className="bg-blue-50 rounded-lg px-4 py-3 border border-blue-100">
                <p className="text-[10px] uppercase tracking-wider text-blue-400 font-semibold mb-1">규격 사양</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">직경</span>
                    <p className="font-semibold text-gray-800">{formData.diameter}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">두께</span>
                    <p className="font-semibold text-gray-800">{formData.thickness}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">하중</span>
                    <p className="font-semibold text-gray-800">{formData.loadClass}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">재질</span>
                    <p className="font-semibold text-gray-800">{formData.material}</p>
                  </div>
                </div>
              </div>

              {/* 후처리 적용 내역 */}
              <div className="bg-amber-50 rounded-lg px-4 py-3 border border-amber-100">
                <p className="text-[10px] uppercase tracking-wider text-amber-500 font-semibold mb-2">후처리 적용</p>
                {selectedPostProcessing.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {selectedPostProcessing.map((opt) => {
                      const Icon = opt.icon;
                      return (
                        <span
                          key={opt.id}
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium bg-white border border-amber-200 text-amber-700"
                        >
                          <Icon className="w-3 h-3" />
                          {opt.label}
                        </span>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-xs text-gray-400">후처리 옵션 없음</p>
                )}
              </div>

              {/* 수량/납기 */}
              <div className="bg-green-50 rounded-lg px-4 py-3 border border-green-100">
                <p className="text-[10px] uppercase tracking-wider text-green-500 font-semibold mb-1">주문 수량</p>
                <p className="text-lg font-bold text-gray-800">
                  {formData.quantity.toLocaleString()}개
                </p>
                <p className="text-xs text-gray-500 mt-0.5">납기: {formData.desiredDelivery}</p>
              </div>
            </div>
          </div>
        </div>

        {/* 확정 견적 */}
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-600" />
            확정 견적
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-gray-600">
              <span>기준 단가</span>
              <span>{formatCurrency(product.basePrice)}</span>
            </div>
            {selectedPostProcessing.map((opt) => (
              <div key={opt.id} className="flex justify-between text-gray-600">
                <span>{opt.label} 추가</span>
                <span>+{formatCurrency(opt.price)}</span>
              </div>
            ))}
            <div className="flex justify-between text-gray-600 border-t border-gray-100 pt-2">
              <span>단가 합계</span>
              <span>{formatCurrency(unitPrice)}</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>수량</span>
              <span>{formData.quantity.toLocaleString()}개</span>
            </div>
            <div className="flex justify-between text-lg font-bold text-gray-900 border-t border-gray-200 pt-3 mt-2">
              <span>확정 합계</span>
              <span className="text-blue-600">{formatCurrency(totalPrice)}</span>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-gray-100">
            <div className="flex justify-between text-sm text-gray-600">
              <span>확정 납기</span>
              <span className="font-medium">주문 확정 후 약 2-3주</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Step 4: Customer Info
// ─────────────────────────────────────────────

function Step4CustomerInfo({
  formData,
  onChange,
  errors,
}: {
  formData: FormData;
  onChange: (field: keyof FormData, value: string) => void;
  errors: Partial<Record<keyof FormData, string>>;
}) {
  const fields: {
    key: keyof FormData;
    label: string;
    type: string;
    placeholder: string;
    required: boolean;
  }[] = [
    { key: "companyName", label: "회사명", type: "text", placeholder: "주식회사 예시", required: true },
    { key: "contactPerson", label: "담당자명", type: "text", placeholder: "홍길동", required: true },
    { key: "phone", label: "연락처", type: "tel", placeholder: "010-1234-5678", required: true },
    { key: "email", label: "이메일", type: "email", placeholder: "example@company.com", required: true },
    { key: "address", label: "배송지 주소", type: "text", placeholder: "서울특별시 강남구 ...", required: true },
  ];

  // 모든 필수 필드가 입력되었는지 확인 (공백만 있는 경우도 비어있는 것으로 취급).
  // 이메일은 "입력 완료" 기준에 형식 검증까지 포함한다.
  const allFilled = fields.every((f) => {
    const v = formData[f.key];
    if (typeof v !== "string" || v.trim().length === 0) return false;
    if (f.key === "email") return isValidEmail(v);
    return true;
  });

  // 이메일 필드 실시간 형식 에러 (입력 중에 바로 피드백)
  const liveEmailError = emailErrorMessage(formData.email);

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-2">주문자 정보 입력</h2>
      <p className="text-sm text-gray-500 mb-4">주문자 정보를 입력해 주세요.</p>

      {/* 필수 입력 안내 배너 — 모든 필드가 입력되어야 "다음" 버튼이 활성화됨 */}
      <div
        className={`mb-6 flex items-start gap-2 rounded-lg border px-4 py-3 text-sm ${
          allFilled
            ? "border-emerald-200 bg-emerald-50 text-emerald-800"
            : "border-amber-200 bg-amber-50 text-amber-800"
        }`}
        role="status"
      >
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
        <p className="leading-relaxed">
          {allFilled ? (
            <>
              주문자 정보 <strong>5가지 항목</strong>이 모두 입력되었습니다. 하단의{" "}
              <strong>&quot;다음&quot;</strong> 버튼을 눌러 다음 단계로 진행해 주세요.
            </>
          ) : (
            <>
              <strong>주문자 정보 5가지 항목(회사명·담당자명·연락처·이메일·배송지 주소)</strong>
              을 모두 입력해야 <strong>&quot;다음&quot;</strong> 버튼이 활성화됩니다.
            </>
          )}
        </p>
      </div>

      <div className="space-y-4">
        {fields.map((field) => {
          // 이메일 필드: 형식 에러는 실시간, 그 외는 validateStep 결과만
          const fieldError =
            field.key === "email"
              ? errors.email ?? liveEmailError ?? null
              : errors[field.key] ?? null;
          const showError = Boolean(fieldError);

          return (
            <div key={field.key}>
              <label
                htmlFor={`customer-${field.key}`}
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <input
                id={`customer-${field.key}`}
                type={field.type}
                value={formData[field.key] as string}
                onChange={(e) => onChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                autoComplete={field.key === "email" ? "email" : undefined}
                inputMode={field.key === "email" ? "email" : undefined}
                aria-invalid={showError}
                aria-describedby={showError ? `customer-${field.key}-error` : undefined}
                className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  showError ? "border-red-400 bg-red-50" : "border-gray-300"
                }`}
              />
              {showError && (
                <p
                  id={`customer-${field.key}-error`}
                  className="mt-1 text-xs text-red-500"
                >
                  {fieldError}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Step 5: Order Complete
// ─────────────────────────────────────────────

function Step5OrderComplete({
  formData,
  product,
  orderNumber,
  onRestart,
}: {
  formData: FormData;
  product: Product;
  orderNumber: string;
  onRestart: () => void;
}) {
  const postProcessingTotal = formData.postProcessing.reduce((sum, id) => {
    const opt = POST_PROCESSING_OPTIONS.find((o) => o.id === id);
    return sum + (opt?.price ?? 0);
  }, 0);
  const unitPrice = product.basePrice + postProcessingTotal;
  const totalPrice = unitPrice * formData.quantity;

  return (
    <div className="text-center">
      <div className="flex justify-center mb-4">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
          <CheckCircle className="w-10 h-10 text-green-500" />
        </div>
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">주문이 접수되었습니다</h2>
      <p className="text-gray-500 mb-6">주문 상태를 이메일로 안내드리겠습니다.</p>

      <div className="bg-blue-50 border border-blue-200 rounded-xl px-6 py-4 mb-6 inline-block">
        <p className="text-sm text-blue-600 mb-1">주문 번호</p>
        <p className="text-2xl font-bold text-blue-800">{orderNumber}</p>
      </div>

      {/* 주문 요약 — 모든 선택 사양을 한눈에 */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 text-left mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">주문 요약</h3>
        <div className="space-y-2.5 text-sm">
          {/* 제품 정보 */}
          <div className="flex justify-between">
            <span className="text-gray-500">제품</span>
            <span className="font-medium text-gray-900">{product.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">규격 (직경/두께)</span>
            <span className="font-medium text-gray-900">
              {formData.diameter} / {formData.thickness}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">재질</span>
            <span className="font-medium text-gray-900">{formData.material}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">하중 등급</span>
            <span className="font-medium text-gray-900">{formData.loadClass}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">수량</span>
            <span className="font-medium text-gray-900">
              {formData.quantity.toLocaleString()}개
            </span>
          </div>

          {/* 후처리 */}
          <div className="flex justify-between">
            <span className="text-gray-500">후처리</span>
            <span className="font-medium text-gray-900">
              {formData.postProcessing.length > 0
                ? POST_PROCESSING_OPTIONS.filter((o) =>
                    formData.postProcessing.includes(o.id)
                  )
                    .map((o) => o.label)
                    .join(", ")
                : "없음"}
            </span>
          </div>

          {/* 희망 납기일 */}
          <div className="flex justify-between">
            <span className="text-gray-500">희망 납기일</span>
            <span className="font-medium text-gray-900">{formData.desiredDelivery}</span>
          </div>

          {/* 확정 금액 */}
          <div className="flex justify-between border-t border-gray-100 pt-2.5">
            <span className="text-gray-500">확정 금액</span>
            <span className="font-bold text-blue-600">{formatCurrency(totalPrice)}</span>
          </div>

          {/* 주문자 정보 */}
          <div className="border-t border-gray-100 pt-2.5 space-y-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">주문자 정보</p>
            <div className="flex justify-between">
              <span className="text-gray-500">회사명</span>
              <span className="font-medium text-gray-900">{formData.companyName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">담당자</span>
              <span className="font-medium text-gray-900">{formData.contactPerson}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">연락처</span>
              <span className="font-medium text-gray-900">{formData.phone}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">이메일</span>
              <span className="font-medium text-gray-900">{formData.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">배송지</span>
              <span className="font-medium text-gray-900 text-right max-w-[60%]">{formData.address}</span>
            </div>
          </div>
        </div>
      </div>

      <p className="text-sm text-gray-500 mb-6">
        담당자가 확인 후 최종 견적을 이메일로 보내드리겠습니다.
        <br />
        문의사항은 고객센터(02-1234-5678)로 연락 주세요.
      </p>

      <button
        onClick={onRestart}
        className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-lg transition-colors"
      >
        <Factory className="w-4 h-4" />
        새 주문하기
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Page Component
// ─────────────────────────────────────────────

const INITIAL_FORM: FormData = {
  selectedProduct: null,
  diameter: "",
  thickness: "",
  loadClass: "",
  material: "",
  postProcessing: [],
  quantity: 10,
  desiredDelivery: "",
  companyName: "",
  contactPerson: "",
  phone: "",
  email: "",
  address: "",
};

export default function CustomerOrderPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [orderNumber, setOrderNumber] = useState("");
  // API 저장 상태
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const selectedProduct = PRODUCTS.find((p) => p.id === formData.selectedProduct) ?? null;

  function handleChange(field: keyof FormData, value: string | string[] | number) {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  }

  function validateStep(currentStep: number): boolean {
    const newErrors: Partial<Record<keyof FormData, string>> = {};

    if (currentStep === 1) {
      if (!formData.companyName) newErrors.companyName = "회사명을 입력해 주세요.";
      if (!formData.contactPerson) newErrors.contactPerson = "담당자명을 입력해 주세요.";
      if (!formData.phone) newErrors.phone = "연락처를 입력해 주세요.";
      if (!formData.email) {
        newErrors.email = "이메일을 입력해 주세요.";
      } else {
        // 형식 검증 (실제 발송 가능한 주소인지는 서버/발송 단계에서 추가 확인)
        const emailErr = emailErrorMessage(formData.email);
        if (emailErr) newErrors.email = emailErr;
      }
      if (!formData.address) newErrors.address = "배송지 주소를 입력해 주세요.";
    }

    if (currentStep === 2) {
      if (!formData.selectedProduct) {
        newErrors.selectedProduct = "제품을 선택해 주세요.";
        return false;
      }
    }

    if (currentStep === 3) {
      if (!formData.diameter) newErrors.diameter = "규격을 선택해 주세요.";
      if (!formData.thickness) newErrors.thickness = "두께를 선택해 주세요.";
      if (!formData.loadClass) newErrors.loadClass = "하중 등급을 선택해 주세요.";
      if (!formData.material) newErrors.material = "재질을 선택해 주세요.";
      if (!formData.desiredDelivery) newErrors.desiredDelivery = "희망 납기일을 입력해 주세요.";
      if (formData.quantity < 10) newErrors.quantity = "최소 주문 수량은 10개입니다.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return false;
    }
    return true;
  }

  async function handleNext() {
    if (!validateStep(step)) return;

    // ─── Step 4(견적 확인) → 5(주문 완료): 백엔드 DB에 주문 저장 ───
    if (step === 4) {
      if (!selectedProduct) return;

      // 단가/합계 계산
      const postProcessingTotal = formData.postProcessing.reduce((sum, id) => {
        const opt = POST_PROCESSING_OPTIONS.find((o) => o.id === id);
        return sum + (opt?.price ?? 0);
      }, 0);
      const unitPrice = selectedProduct.basePrice + postProcessingTotal;
      const totalPrice = unitPrice * formData.quantity;

      const orderId = generateOrderNumber();
      // customer_id: 이메일 앞부분 + 타임스탬프 뒷 4자리로 간단 생성
      const customerId = `CUST-${Date.now().toString().slice(-6)}`;

      try {
        setSubmitting(true);
        setSubmitError(null);

        // 1) 주문 헤더 저장 (email 을 전용 컬럼으로 저장)
        const orderRes = await fetch("/api/orders", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: orderId,
            customer_id: customerId,
            customer_name: formData.contactPerson,
            company_name: formData.companyName,
            contact: formData.phone,
            email: formData.email,
            shipping_address: formData.address,
            total_amount: totalPrice,
            status: "pending",
            requested_delivery: formData.desiredDelivery,
            confirmed_delivery: null,
          }),
        });

        if (!orderRes.ok) {
          const errBody = await orderRes.json().catch(() => ({}));
          throw new Error(
            typeof errBody.detail === "string"
              ? errBody.detail
              : "주문 저장에 실패했습니다. 백엔드 서버를 확인해 주세요."
          );
        }

        // 2) 주문 품목 상세 저장
        const postProcessingLabel =
          formData.postProcessing.length > 0
            ? formData.postProcessing
                .map(
                  (id) =>
                    POST_PROCESSING_OPTIONS.find((o) => o.id === id)?.label ?? id
                )
                .join(", ")
            : null;

        const detailRes = await fetch(`/api/orders/${orderId}/details`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: `${orderId}-DET-001`,
            order_id: orderId,
            product_id: selectedProduct.id,
            product_name: selectedProduct.name,
            quantity: formData.quantity,
            spec: `직경 ${formData.diameter} / 두께 ${formData.thickness} / 하중 ${formData.loadClass}`,
            material: formData.material,
            post_processing: postProcessingLabel,
            logo_data: null,
            unit_price: unitPrice,
            subtotal: totalPrice,
          }),
        });

        if (!detailRes.ok) {
          throw new Error("주문 품목 상세 저장에 실패했습니다.");
        }

        // 저장 성공 → 서버 확정 ID 사용
        setOrderNumber(orderId);
      } catch (err) {
        setSubmitError(
          err instanceof Error
            ? err.message
            : "알 수 없는 오류가 발생했습니다."
        );
        return; // 실패 시 Step 5로 넘어가지 않음
      } finally {
        setSubmitting(false);
      }
    }

    setStep((prev) => Math.min(prev + 1, 5));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handlePrev() {
    setErrors({});
    setStep((prev) => Math.max(prev - 1, 1));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleRestart() {
    setFormData(INITIAL_FORM);
    setErrors({});
    setStep(1);
    setOrderNumber("");
    setSubmitError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Step 1 (주문자 정보) 의 5개 필수 필드가 모두 채워지고
  // 이메일 형식도 유효해야 "다음" 버튼이 활성화된다.
  const isStep1Valid =
    formData.companyName.trim().length > 0 &&
    formData.contactPerson.trim().length > 0 &&
    formData.phone.trim().length > 0 &&
    isValidEmail(formData.email) &&
    formData.address.trim().length > 0;

  // 현재 단계 기준으로 "다음" / "주문 제출" 버튼을 비활성화해야 하는가?
  const nextDisabled = submitting || (step === 1 && !isStep1Valid);

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-50 via-orange-50 to-red-50">
      <SmartCastHeader variant="card" />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-24 pb-8">
      {/* Step indicator */}
      <StepIndicator currentStep={step} />

      {/* Card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sm:p-8">
        {step === 1 && (
          <Step4CustomerInfo
            formData={formData}
            onChange={(field, value) => handleChange(field, value)}
            errors={errors}
          />
        )}
        {step === 2 && (
          <Step1ProductSelection
            selectedProduct={formData.selectedProduct}
            onSelect={(id) => {
              handleChange("selectedProduct", id);
              setFormData((prev) => ({
                ...prev,
                selectedProduct: id,
                diameter: "",
                thickness: "",
              }));
            }}
          />
        )}
        {step === 3 && selectedProduct && (
          <Step2SpecInput
            formData={formData}
            product={selectedProduct}
            onChange={handleChange}
            errors={errors}
          />
        )}
        {step === 4 && selectedProduct && (
          <Step3QuoteReview formData={formData} product={selectedProduct} />
        )}
        {step === 5 && selectedProduct && (
          <Step5OrderComplete
            formData={formData}
            product={selectedProduct}
            orderNumber={orderNumber}
            onRestart={handleRestart}
          />
        )}

        {/* Navigation buttons */}
        {step < 5 && (
          <div className="mt-8 pt-6 border-t border-gray-100">
            {/* 에러 메시지 */}
            {submitError && (
              <div className="flex items-start gap-2 mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{submitError}</span>
              </div>
            )}

            <div className="flex items-center justify-between">
              <button
                onClick={handlePrev}
                disabled={step === 1 || submitting}
                className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all ${
                  step === 1 || submitting
                    ? "text-gray-300 cursor-not-allowed"
                    : "text-gray-600 hover:bg-gray-100 border border-gray-200"
                }`}
              >
                <ChevronLeft className="w-4 h-4" />
                이전
              </button>

              <span className="text-xs text-gray-400">
                {step} / {STEPS.length - 1}단계
              </span>

              <button
                onClick={handleNext}
                disabled={nextDisabled}
                title={
                  step === 1 && !isStep1Valid
                    ? "주문자 정보 5가지 항목(회사명·담당자명·연락처·이메일·배송지 주소)을 모두 입력해 주세요."
                    : undefined
                }
                className={`inline-flex items-center gap-2 font-medium px-6 py-2.5 rounded-lg transition-all shadow-sm ${
                  nextDisabled
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700 text-white hover:shadow-md"
                }`}
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    저장 중...
                  </>
                ) : (
                  <>
                    {step === 4 ? "주문 제출" : "다음"  /* step 4 = 견적 확인 → 주문 완료 */}
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
      </div>
    </div>
  );
}
