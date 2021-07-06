import chalk from 'chalk'

import { sleep } from './util'

export async function response (getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()

    const delay = getArgs.delay || 800
    delay && await sleep(delay)

    const invoke = getArgs.invoke
    switch (invoke) {
        default:
            return {
                code: 1,
                result: false,
                data: null,
                message: 'failed'
            }
    }
}
