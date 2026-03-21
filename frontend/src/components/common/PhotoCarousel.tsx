import { useCallback } from 'react';
import useEmblaCarousel from 'embla-carousel-react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PhotoCarouselProps {
  photos: string[];
  altPrefix: string;
}

export function PhotoCarousel({ photos, altPrefix }: PhotoCarouselProps) {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true });

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  if (photos.length === 0) {
    return (
      <div className="aspect-video w-full bg-gradient-to-br from-teal-100 to-teal-300" />
    );
  }

  return (
    <div className="relative">
      <div ref={emblaRef} className="overflow-hidden">
        <div className="flex">
          {photos.map((photo, idx) => (
            <div key={idx} className="min-w-0 flex-[0_0_100%]">
              <img
                src={photo}
                alt={`${altPrefix} - photo ${idx + 1}`}
                className="aspect-video w-full object-cover"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Navigation buttons */}
      {photos.length > 1 && (
        <>
          <Button
            variant="ghost"
            size="icon"
            onClick={scrollPrev}
            className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-white/80 shadow-md hover:bg-white"
            aria-label="Previous photo"
          >
            <ChevronLeft className="size-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={scrollNext}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-white/80 shadow-md hover:bg-white"
            aria-label="Next photo"
          >
            <ChevronRight className="size-5" />
          </Button>

          {/* Dot indicators */}
          <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 gap-1.5">
            {photos.map((_, idx) => (
              <button
                key={idx}
                onClick={() => emblaApi?.scrollTo(idx)}
                className="size-2 rounded-full bg-white/60 transition-colors hover:bg-white"
                aria-label={`Go to photo ${idx + 1}`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
