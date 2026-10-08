//! Port of `src/execution/executor_factory.cpp`: the executor for a plan node. Given code. (The executors that the course's modules ask
//! you to write are created here too, once they exist.)

use super::executor_context::ExecutorContext;
use super::executors::abstract_executor::ExecutorBox;
use super::executors::filter_executor::FilterExecutor;
use super::executors::mock_scan_executor::MockScanExecutor;
use super::executors::projection_executor::ProjectionExecutor;
use super::executors::values_executor::ValuesExecutor;
use super::plans::plan_node::{PlanRef, PlanType};
use crate::common::exception::{Exception, ExceptionType, Result};

pub fn create_executor<'e>(ctx: &'e ExecutorContext<'e>, plan: &PlanRef) -> Result<ExecutorBox<'e>> {
    match plan.plan_type() {
        PlanType::MockScan => Ok(Box::new(MockScanExecutor::new(plan.clone()))),
        PlanType::Projection => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(ProjectionExecutor::new(plan.clone(), child)))
        }
        PlanType::Filter => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(FilterExecutor::new(plan.clone(), child)))
        }
        PlanType::Values => Ok(Box::new(ValuesExecutor::new(plan.clone()))),
        other => Err(Exception::new(ExceptionType::NotImplemented, format!("there is no executor for {other:?} plans (yet)"))),
    }
}
