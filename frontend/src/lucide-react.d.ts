declare module 'lucide-react' {
  import type { ComponentType, SVGProps } from 'react'

  export interface LucideProps extends SVGProps<SVGSVGElement> {
    size?: number | string
    absoluteStrokeWidth?: boolean
  }

  export const Download: ComponentType<LucideProps>
  export const Footprints: ComponentType<LucideProps>
  export const Minus: ComponentType<LucideProps>
  export const Play: ComponentType<LucideProps>
  export const Plus: ComponentType<LucideProps>
  export const RotateCcw: ComponentType<LucideProps>
  export const Search: ComponentType<LucideProps>
  export const ShieldAlert: ComponentType<LucideProps>
  export const ShieldCheck: ComponentType<LucideProps>
  export const Star: ComponentType<LucideProps>
  export const Upload: ComponentType<LucideProps>
  export const X: ComponentType<LucideProps>
}
