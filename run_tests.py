import unittest
import sys
import coverage

def run_tests(with_coverage=False):
    """运行所有测试"""
    if with_coverage:
        # 启动代码覆盖率统计
        cov = coverage.Coverage(
            branch=True,
            include=['app/*'],
            omit=['tests/*', 'migrations/*']
        )
        cov.start()

    # 发现并运行所有测试
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if with_coverage:
        # 停止覆盖率统计并生成报告
        cov.stop()
        cov.save()
        print('\n代码覆盖率报告:')
        cov.report()
        cov.html_report(directory='coverage_report')
        print('\n详细的HTML覆盖率报告已生成到 coverage_report 目录')

    return result.wasSuccessful()

if __name__ == '__main__':
    # 检查是否需要生成覆盖率报告
    with_coverage = '--coverage' in sys.argv
    
    print('开始运行测试...\n')
    success = run_tests(with_coverage)
    
    # 根据测试结果设置退出码
    sys.exit(not success)