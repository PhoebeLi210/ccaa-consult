import { useState, useEffect } from 'react';

/** 响应式断点结果 */
interface ResponsiveResult {
  /** 是否为移动端（屏幕宽度 < 768px） */
  isMobile: boolean;
  /** 是否为PC端（屏幕宽度 >= 768px） */
  isPc: boolean;
  /** 当前窗口宽度 */
  width: number;
}

/** 移动端断点阈值 */
const MOBILE_BREAKPOINT = 768;

/**
 * 响应式断点Hook
 * 监听窗口尺寸变化，判断当前是移动端还是PC端
 * @returns {ResponsiveResult} 包含isMobile、isPc和width的对象
 */
export function useResponsive(): ResponsiveResult {
  const [windowSize, setWindowSize] = useState<{
    width: number;
    height: number;
  }>(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
  }));

  useEffect(() => {
    /** 窗口尺寸变化处理函数 */
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);

    // 初始化时立即执行一次
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return {
    isMobile: windowSize.width < MOBILE_BREAKPOINT,
    isPc: windowSize.width >= MOBILE_BREAKPOINT,
    width: windowSize.width,
  };
}

export default useResponsive;
